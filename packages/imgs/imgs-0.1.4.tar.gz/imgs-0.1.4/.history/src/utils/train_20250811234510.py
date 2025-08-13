# import json
# import logging
# import os
# from dataclasses import dataclass, field
# from typing import override

# from PIL import Image, PngImagePlugin

# # Increase the limit to 10MB (adjust as needed)
# PngImagePlugin.MAX_TEXT_CHUNK = 10 * (1024**2)
# # Disable tokenizers parallelism warning in multiprocessing environments
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# import torch
# from datasets import load_dataset
# from torch.utils.data import Dataset
# from transformers import (
#     AutoProcessor,
#     CLIPModel,
#     Trainer,
#     TrainingArguments,
#     set_seed,
# )
# from trl import ScriptArguments, TrlParser

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# @dataclass
# class ClipTrainingArguments(ScriptArguments):
#     """Extended script arguments for CLIP training on ImageNet."""

#     model_name_or_path: str = field(
#         default="openai/clip-vit-large-patch14-336",
#         metadata={"help": "CLIP model name from HuggingFace"},
#     )
#     wnid_to_classname_path: str = field(
#         default="modified_wnid2classname.json",
#         metadata={"help": "Path to the WNID to class name mapping file"},
#     )
#     max_train_samples: int | None = field(
#         default=None, metadata={"help": "Maximum number of training samples to use (for debugging)"}
#     )
#     max_eval_samples: int | None = field(
#         default=None,
#         metadata={"help": "Maximum number of evaluation samples to use (for debugging)"},
#     )
#     freeze_vision_model: bool = field(
#         default=False, metadata={"help": "Whether to freeze the vision encoder"}
#     )
#     freeze_text_model: bool = field(
#         default=False, metadata={"help": "Whether to freeze the text encoder"}
#     )
#     preprocessing_num_workers: int = field(
#         default=4, metadata={"help": "Number of workers for data preprocessing"}
#     )


# class ImageNetCLIPDataset(Dataset):
#     """Dataset for ImageNet CLIP training with 'a photo of [class_name]' templates."""

#     def __init__(self, dataset, processor, class_names, split="train"):
#         self.dataset = dataset
#         self.processor = processor
#         self.class_names = class_names
#         self.split = split

#     def __len__(self):
#         return len(self.dataset)

#     @override
#     def __getitem__(self, idx):
#         item = self.dataset[idx]
#         image = item["image"]
#         class_id = item["label"]
#         class_name = self.class_names[class_id]
#         caption = f"a photo of {class_name}"

#         # Process image and text
#         inputs = self.processor(
#             text=caption,
#             images=image,
#             return_tensors="pt",
#             padding="max_length",
#             truncation=True,
#             max_length=77,
#         )

#         # Remove batch dimension
#         return {
#             "pixel_values": inputs["pixel_values"].squeeze(0),
#             "input_ids": inputs["input_ids"].squeeze(0),
#             "attention_mask": inputs["attention_mask"].squeeze(0),
#         }


# def load_class_names(wnid_to_classname_path):
#     """Load class names from WNID mapping file."""
#     with open(wnid_to_classname_path) as f:
#         wnid_to_classname = json.load(f)

#     # Convert to a simple list where index corresponds to ImageNet class ID
#     class_names = list(wnid_to_classname.values())

#     logger.info(f"Loaded {len(class_names)} class names")
#     return class_names


# def collate_fn(batch):
#     """Collate function for DataLoader."""
#     pixel_values = torch.stack([item["pixel_values"] for item in batch])
#     input_ids = torch.stack([item["input_ids"] for item in batch])
#     attention_mask = torch.stack([item["attention_mask"] for item in batch])

#     return {
#         "pixel_values": pixel_values,
#         "input_ids": input_ids,
#         "attention_mask": attention_mask,
#         "return_loss": True,
#     }


# def main():
#     parser = TrlParser((ClipTrainingArguments, TrainingArguments))
#     clip_args, training_args = parser.parse_args_and_config()

#     # Set up logging
#     logging.basicConfig(
#         format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
#         datefmt="%m/%d/%Y %H:%M:%S",
#         level=logging.INFO,
#     )

#     logger.info(f"Training arguments: {training_args}")
#     logger.info(f"CLIP arguments: {clip_args}")

#     # Set seed
#     set_seed(training_args.seed)

#     # Load class names
#     logger.info("Loading class names...")
#     class_names = load_class_names(clip_args.wnid_to_classname_path)

#     # Load model and processor
#     logger.info(f"Loading CLIP model: {clip_args.model_name_or_path}")
#     model = CLIPModel.from_pretrained(clip_args.model_name_or_path)
#     processor = AutoProcessor.from_pretrained(clip_args.model_name_or_path)

#     # Freeze model parts if requested
#     if clip_args.freeze_vision_model:
#         logger.info("Freezing vision model")
#         for param in model.vision_model.parameters():
#             param.requires_grad = False

#     if clip_args.freeze_text_model:
#         logger.info("Freezing text model")
#         for param in model.text_model.parameters():
#             param.requires_grad = False

#     # Print trainable parameters info
#     total_params = sum(p.numel() for p in model.parameters())
#     trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
#     logger.info(
#         f"Total params: {total_params:,} | Trainable: {trainable_params:,} ({100 * trainable_params / total_params:.1f}%)"
#     )

#     # Load datasets
#     logger.info("Loading ImageNet dataset...")
#     dataset = load_dataset(clip_args.dataset_name)

#     # Prepare train dataset
#     train_dataset = dataset["train"]
#     if clip_args.max_train_samples:
#         train_dataset = train_dataset.select(range(clip_args.max_train_samples))

#     train_dataset = ImageNetCLIPDataset(train_dataset, processor, class_names, "train")
#     logger.info(f"Training dataset size: {len(train_dataset)}")

#     # Initialize trainer
#     trainer = Trainer(
#         model=model,
#         args=training_args,
#         train_dataset=train_dataset,
#         processing_class=processor,
#         data_collator=collate_fn,
#     )

#     logger.info("Starting training...")
#     train_result = trainer.train()

#     # Save model
#     trainer.save_model()
#     processor.save_pretrained(training_args.output_dir)

#     # Log metrics
#     trainer.log_metrics("train", train_result.metrics)
#     trainer.save_metrics("train", train_result.metrics)
#     trainer.save_state()

#     logger.info("Training completed!")


# if __name__ == "__main__":
#     main()
