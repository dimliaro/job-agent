"""
The orchestrator. Run:  python agent.py

Pipeline (v1 is a linear pipeline, not a full tool-calling agent — that's
deliberate: get the pieces working first, add the agentic loop later):

  1. load jobs
  2. score each against the profile
  3. keep the ones above MIN_SCORE, take the top N
  4. tailor the CV for each kept job -> output/
  5. email (or print) a digest
"""

import os
import config
import sources
import llm
import notify
import export


def load_master_cv() -> str:
    with open(config.MASTER_CV_PATH, "r", encoding="utf-8") as f:
        return f.read()


def slug(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-")


def main() -> None:
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    master_cv = load_master_cv()

    jobs = sources.get_jobs()
    print(f"Loaded {len(jobs)} jobs (source: {config.SOURCE}).")

    if not jobs:
        notify.send_digest("No jobs returned from the source today.")
        return

    # Score everything.
    scored = []
    for job in jobs:
        result = llm.score_job(job, config.PROFILE)
        job["_score"] = result.get("score", 0)
        job["_reasons"] = result.get("reasons", "")
        print(f"  {job['_score']:>3}  {job['title']} @ {job['company']}")
        scored.append(job)

    # Keep the good ones, best first.
    kept = [j for j in scored if j["_score"] >= config.MIN_SCORE]
    kept.sort(key=lambda j: j["_score"], reverse=True)
    kept = kept[: config.TOP_N]

    if not kept:
        notify.send_digest("No jobs cleared the score threshold today.")
        return

    # Tailor a CV for each kept job.
    lines = ["Top matches:\n"]
    for job in kept:
        cv = llm.tailor_cv(master_cv, job)
        base = os.path.join(config.OUTPUT_DIR, f"cv-{slug(job['company'])}-{job['id']}")
        md_path = base + ".md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(cv)
        docx_path = export.markdown_cv_to_docx(cv, base + ".docx")
        lines.append(
            f"[{job['_score']}] {job['title']} @ {job['company']}\n"
            f"    {job['location']}\n"
            f"    {job['url']}\n"
            f"    why: {job['_reasons']}\n"
            f"    tailored CV: {docx_path}  (also {md_path})\n"
        )

    notify.send_digest("\n".join(lines))


if __name__ == "__main__":
    main()
