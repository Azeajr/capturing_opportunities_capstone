import pandas as pd
from matplotlib import pyplot as plt
from pathlib import Path


def main():
    Path("charts").mkdir(exist_ok=True)

    correlated_df = pd.read_csv("correlated_data.csv")

    models_used = correlated_df["model_used"].unique()

    questions = [
        "I think that I would like to use this system frequently.",
        "I found the system unnecessarily complex.",
        "I thought the system was easy to use.",
        "I think that I would need the support of a technical person to be able to use this system.",
        "I found the various functions in this system were well integrated.",
        "I thought there was too much inconsistency in this system.",
        "I would imagine that most people would learn to use this system very quickly.",
        "I found the system very cumbersome to use.",
        "I felt very confident using the system.",
        "I needed to learn a lot of things before I could get going with this system.",
    ]

    for model in models_used:
        df = correlated_df[correlated_df["model_used"] == model]
        print(f"Model: {model}")
        for idx, question in enumerate(questions):
            question_data = df[question].dropna().astype(int)
            score_counts = question_data.value_counts().reindex(
                range(1, 6), fill_value=0
            )

            plt.figure(figsize=(8, 5))
            score_counts.plot(kind="bar", color="skyblue")
            plt.title(f"{model} - {question}")
            plt.xlabel("User Ratings")
            plt.ylabel("Number of Responses")
            plt.tight_layout()
            # plt.show()
            plt.savefig(f"charts/{model}_{idx + 1}.png", bbox_inches="tight")
            plt.close()


if __name__ == "__main__":
    main()
