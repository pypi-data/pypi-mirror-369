from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

# Load model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=100,
    evaluation_strategy="epoch",
    save_strategy="epoch",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    processing_class=tokenizer,
)

# methods you can use
trainer.pop_callback()
trainer.remove_callback()
trainer.get_num_trainable_parameters()
trainer.get_learning_rates()
trainer.floating_point_ops()

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
