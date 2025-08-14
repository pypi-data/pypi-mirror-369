from pathlib import Path

from pipeloom import TaskDef, run_pipeline


def test_smoke(tmp_path: Path):
    """A very light smoke test that ensures the demo pipeline runs and creates a DB."""
    db = tmp_path / "demo.db"
    tasks = [TaskDef(task_id=i, name=f"t{i}", steps=5) for i in range(1, 6)]
    run_pipeline(db, tasks, workers=2, wal=True, store_task_status=True)
    assert db.exists()
