import os
import argparse
import ollama
import time
from friday.generative import generator_sentences

if __name__ == "__main__":
    # Parse degli argomenti da riga di comando
    parser = argparse.ArgumentParser(description="Genera frasi in inglese per poi tradurle e parafrasarle")
    parser.add_argument("topic", type=str,
                        help="Argomento della generazione")
    parser.add_argument("number", type=int,
                        help="Numero di frasi")
    args = parser.parse_args()
    generator_sentences(args.topic, args.number, 0)
