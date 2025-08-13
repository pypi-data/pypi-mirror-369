from transformers import (
    AutoConfig,
    AutoModel,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

# Load model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    processing_class=tokenizer,
)

config = AutoConfig.from_pretrained(pretrained_model_name_or_path="bert-base-uncased")
model = AutoModel.from_config(config)
model_size = sum(t.numel() for t in model.parameters())
print(f"Model size: {model_size / 1000**2:.1f}M parameters")
# methods you can use
trainer.pop_callback()
trainer.remove_callback()
trainer.get_num_trainable_parameters()
trainer.get_learning_rates()
trainer.floating_point_ops(inputs=inputs)
trainer.init_hf_repo()
trainer.create_model_card()
trainer.push_to_hub()


# methods that you may need to modify
train_dataloader = trainer.get_train_dataloader()
eval_dataloader = trainer.get_eval_dataloader()
trainer.create_optimizer()
trainer.create_scheduler(num_training_steps=num_training_steps, optimizer=optimizer)
trainer.log(logs=logs, start_time=start_time)
trainer.training_step(model=model, inputs=inputs, num_items_in_batch=num_items_in_batch)
trainer.compute_loss(
    model=model, inputs=inputs, return_outputs=return_outputs, num_items_in_batch=num_items_in_batch
)
trainer.save_model()
trainer.evaluate()
trainer.evaluation_loop()
trainer.predict()
trainer.prediction_step()


trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)
