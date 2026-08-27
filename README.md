# ContextTurbine

ContextTurbine repeatedly compresses local-agent state and measures exactly which required facts survive each round. It works against a local OpenAI-compatible endpoint or recorded responses for reproducible CI.

```bash
python -m contextturbine examples/spec.json --responses examples/responses.json --fail-on-loss
python -m contextturbine case.json --endpoint http://127.0.0.1:8080 --model local-gguf
```

Reports include characters, source compression ratio, exact required-fact survival, token recall, and the first loss round. Recorded responses separate measurement from model nondeterminism. The evaluator uses normalized phrase presence; it does not claim semantic equivalence or prove that an omitted fact was unimportant.

Live mode sends the supplied state to the endpoint you choose. The default is localhost; inspect the endpoint before using private state.

## Test

`python -m unittest discover -s tests -v`

## Fund more development

Donations increase RequiredTruth development production. See [SUPPORT.md](SUPPORT.md); confirmed donors may claim a transaction hash in an issue and request a specific direction.

Apache-2.0 licensed.


## Install and run

```sh
chmod +x install.sh run.sh
./install.sh
./run.sh --help
```


## Standard launcher

`./run.sh` is the normal entry point. It runs `./install.sh` automatically when setup is missing, then opens the PySide6 control panel with live output and actions for the demo, tests, repair, and stop. Use `./cli.sh` for CLI-only operation.
