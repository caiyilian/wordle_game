from fastapi import FastAPI


app = FastAPI(title="Wordle Game API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
