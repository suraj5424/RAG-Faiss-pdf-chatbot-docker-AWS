import torch
from transformers import AutoTokenizer, AutoModel
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantFormat, QuantType
import os

def convert_to_onnx_and_quantize(model_name: str, output_dir: str):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define file paths
    onnx_path = os.path.join(output_dir, "model.onnx")
    quantized_onnx_path = os.path.join(output_dir, "model_quantized.onnx")

    print(f"✅ Loading model and tokenizer for: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    # Set the model to evaluation mode
    model.eval()

    # --- 1. Export to ONNX ---
    
    # Create a dummy input for tracing
    # all-MiniLM-L6-v2 model takes input_ids, token_type_ids, and attention_mask
    dummy_input = tokenizer("This is a dummy sentence for ONNX export.", return_tensors="pt")
    
    print(f"⚙️ Exporting model to ONNX format at: {onnx_path}")
    torch.onnx.export(
        model,
        (dummy_input['input_ids'], dummy_input['attention_mask']),
        f=onnx_path,
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "last_hidden_state": {0: "batch_size", 1: "sequence_length"},
        },
        opset_version=14,
    )
    
    print(f"✅ Successfully exported ONNX model.")

    # --- 2. Quantize the ONNX model ---
    
    print(f"📊 Quantizing ONNX model to: {quantized_onnx_path}")
    quantize_dynamic(
        model_input=onnx_path,
        model_output=quantized_onnx_path,
        per_channel=True,
        reduce_range=True,
        activation_type=QuantType.QUInt8,
        weight_type=QuantType.QInt8,
        optimize_model=True
    )
    
    print(f"✅ Successfully quantized ONNX model.")
    
    # --- 3. Verify the models ---
    print("\n--- Model Verification ---")
    
    # Verify the ONNX model
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    print(f"Original ONNX model is valid.")
    
    # Verify the Quantized ONNX model
    quantized_model = onnx.load(quantized_onnx_path)
    onnx.checker.check_model(quantized_model)
    print(f"Quantized ONNX model is valid.")
    
    # Compare file sizes
    original_size = os.path.getsize(onnx_path)
    quantized_size = os.path.getsize(quantized_onnx_path)
    print(f"Original ONNX size: {original_size / 1024 / 1024:.2f} MB")
    print(f"Quantized ONNX size: {quantized_size / 1024 / 1024:.2f} MB")
    
    print("\n🎉 Process complete!")
    print(f"Models saved in: {output_dir}")

if __name__ == "__main__":
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    OUTPUT_DIRECTORY = "./onnx_quantized_models"
    convert_to_onnx_and_quantize(MODEL_NAME, OUTPUT_DIRECTORY)