#!/usr/bin/env python3
# main.py - llm_optimizer

import torch
import gc
import time
import csv
import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer
from codecarbon import EmissionsTracker
import evaluate


def load_and_generate(
    model_name: str,
    questions: list,
    references: list = None,
    output_csv: str = "results.csv",
    max_length: int = 80,
    prune_threshold: float = 1e-3
) -> None:
    """
    Run LLM inference with pruning + freezing optimization and track CO2.
    References are optional.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load model & tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device).eval()

    # Load metrics (only if references are given)
   
    try:
        perplexity_metric = evaluate.load(
            "perplexity",
            module_type="metric",
            model_id=model_name )
    except Exception:
        perplexity_metric = None

    bleu_metric = evaluate.load("bleu") if references else None
    rouge_metric = evaluate.load("rouge") if references else None


    # === Freezing ===
    frozen_layer_names = []

    def freeze_hook(module, input, output, layer_name):
        return torch.where(torch.abs(output) < 1e-4, torch.zeros_like(output), output)

    def apply_freeze_hooks(m):
        for name, module in m.named_modules():
            if 'mlp' in name and hasattr(module, 'forward'):
                module.register_forward_hook(
                    lambda mod, inp, out, n=name: freeze_hook(mod, inp, out, n)
                )
                frozen_layer_names.append(name)

    # === Pruning ===
    def self_prune(m, threshold=1e-3):
        with torch.no_grad():
            for name, param in m.named_parameters():
                if 'weight' in name and len(param.shape) > 1:
                    mask = param.abs() > threshold
                    param.mul_(mask.float())

    # === Memory cleanup ===
    def free_gpu_memory():
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        gc.collect()

    free_gpu_memory()

    # === Caching for repeated prompts ===
    prompt_cache = {}

    def cached_infer(prompt):
        if prompt in prompt_cache:
            return prompt_cache[prompt]
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=max_length)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        prompt_cache[prompt] = result
        return result

    def evaluate_model(prompt, reference=None):
        generated = cached_infer(prompt)
        ppl = perplexity_metric.compute(
    predictions=[generated]
)["perplexities"][0]
        bleu = rouge = None
        if reference:
            bleu = bleu_metric.compute(
                predictions=[generated], references=[reference]
            )["bleu"]
            rouge = rouge_metric.compute(
                predictions=[generated], references=[reference]
            )["rougeL"]
        return ppl, bleu, rouge, generated

    # === Apply optimizations ===
    self_prune(model, threshold=prune_threshold)
    apply_freeze_hooks(model)

    # === CO₂ Tracking ===
    tracker_opt = EmissionsTracker(project_name="optimized_run", output_file=None)
    tracker_opt.start()
    start_time = time.time()

    results = []
    if references:
        for prompt, ref in zip(questions, references):
            ppl, bleu, rouge, output = evaluate_model(prompt, ref)
            results.append({
                "Prompt": prompt,
                "Generated": output,
                "Perplexity": round(ppl, 4),
                "BLEU": round(bleu, 4) if bleu is not None else None,
                "ROUGE-L": round(rouge, 4) if rouge is not None else None
            })
    else:
        for prompt in questions:
            ppl, _, _, output = evaluate_model(prompt)
            results.append({
                "Prompt": prompt,
                "Generated": output,
                "Perplexity": round(ppl, 4),
                "BLEU": None,
                "ROUGE-L": None
            })

    end_time = time.time()
    emissions_opt = tracker_opt.stop()
    total_time = end_time - start_time

    # Add stats to each row
    for r in results:
        r["Total_CO2_kg"] = round(emissions_opt, 6)
        r["Total_Inference_Time_s"] = round(total_time, 2)

    # === Save results ===
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n=== OPTIMIZED RUN RESULTS ===")
    print(f"CSV saved to: {output_csv}")
    print(f"Total Prompts: {len(questions)}")
    print(f"Total Inference Time: {total_time:.2f}s")
    print(f"Total CO₂ Emissions: {emissions_opt:.6f} kg\n")

    return {
        "total_time": total_time,
        "total_co2": emissions_opt,
        "results": results
    }


# === CLI ENTRY POINT ===
def main():
    parser = argparse.ArgumentParser(description="LLM Optimizer with CO₂ Tracking")
    parser.add_argument("--model", type=str, required=True, help="HuggingFace model name")
    parser.add_argument("--prompts", type=str, nargs="+", required=True, help="List of prompts")
    parser.add_argument("--references", type=str, nargs="*", help="List of reference answers (optional)")
    parser.add_argument("--output", type=str, default="results.csv", help="Output CSV file name")
    parser.add_argument("--max_length", type=int, default=80, help="Max length for generation")
    parser.add_argument("--prune_threshold", type=float, default=1e-3, help="Pruning threshold")
    args = parser.parse_args()

    if args.references and len(args.prompts) != len(args.references):
        raise ValueError("Number of prompts and references must be the same if references are given.")

    load_and_generate(
        model_name=args.model,
        questions=args.prompts,
        references=args.references if args.references else None,
        output_csv=args.output,
        max_length=args.max_length,
        prune_threshold=args.prune_threshold
    )


if __name__ == "__main__":
    main()
