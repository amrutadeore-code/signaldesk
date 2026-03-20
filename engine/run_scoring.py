from engine.scoring_engine import run_scoring


def main():
    results = run_scoring()

    print("\nSignalDesk scoring run completed.\n")
    for row in results:
        print(
            f"{row['account_name']}: "
            f"score={row['total_score']}, "
            f"band={row['risk_band']}, "
            f"drivers=[{row['top_driver_1']}, {row['top_driver_2']}, {row['top_driver_3']}]"
        )


if __name__ == "__main__":
    main()