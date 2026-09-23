kaggle kernels pull auraecosystem/kaggle-854ccca8a132
git clone https://github.com/web4hub/OmniSkel-AI.git
cd OmniSkel-AI
uv run huggingface-cli login
uv run cb docker build
REV=chi-bench-v1.0.0
uv run huggingface-cli download actava/chi-bench \
  --repo-type dataset --revision "$REV" --local-dir data/
echo "$REV" > data/.chi-bench-version
# Schema + preflight: dataset pin, Modal/Docker, agent name
uv run cb submission validate -f configs/submissions/<your-id>.yaml

# Run all 3 domains. Default: one trial per task (pass@1).
uv run cb submission run      -f configs/submissions/<your-id>.yaml

# Check progress; safe to run while `submission run` is in flight.
uv run cb submission status   -f configs/submissions/<your-id>.yaml

# Curate the leaderboard-ready packet.
uv run cb submission prepare  -f configs/submissions/<omniskel-ai>.yaml
gh auth login
gh repo fork actava-ai/leaderboard --clone=false
git clone https://github.com/<web4hub>/leaderboard && cd leaderboard
cp -r /path/to/packet/2026-05-13-<slug>/ benchmarks/<bench>/submissions/
python scripts/validate.py benchmarks/<bench>/submissions/2026-05-13-<slug>/
git checkout -b sub/<bench>/2026-05-13-<slug>
git commit -am "<bench>: <team> · <agent> · <model>"
git push origin sub/<bench>/2026-05-13-<slug>
gh pr create -R actava-ai/leaderboard --base main
cp .env.example .env
docker compose -f infra/docker-compose.yml up --build
