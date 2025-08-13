from typing import Any, Literal

from transformers.trainer_callback import TrainerCallback

from .progress import OnLogCallback, OnProgressCallback, safely_call_on_progress


def optional_callbacks(*cbs: TrainerCallback | None) -> list[TrainerCallback]:
    return [cb for cb in cbs if cb is not None]


class ProgressCallback(TrainerCallback):
    def __init__(self, on_progress: OnProgressCallback, mode: Literal["predict", "train"]):
        self.progress_callback = on_progress
        self.mode = mode
        self.prediction_step = 0

    def on_prediction_step(self, args, state, control, eval_dataloader: Any = None, **kwargs):
        if self.mode == "predict":
            safely_call_on_progress(self.progress_callback, self.prediction_step, len(eval_dataloader))
            self.prediction_step += 1

    def on_evaluate(self, args, state, control, eval_dataloader: Any = None, **kwargs):
        if self.mode == "predict":
            # sanity check that this is called at the end of the eval loop
            assert len(eval_dataloader) == self.prediction_step
            safely_call_on_progress(self.progress_callback, len(eval_dataloader), len(eval_dataloader))
            # reset the prediction step counter
            self.prediction_step = 0

    def on_train_begin(self, args, state, control, **kwargs):
        if self.mode == "train":
            safely_call_on_progress(self.progress_callback, state.global_step, state.max_steps)

    def on_step_end(self, args, state, control, **kwargs):
        if self.mode == "train":
            safely_call_on_progress(self.progress_callback, state.global_step, state.max_steps)


class LoggingCallback(TrainerCallback):
    def __init__(self, on_log: OnLogCallback):
        self.log_callback = on_log

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is not None:
            self.log_callback(logs)
