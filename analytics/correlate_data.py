import pandas as pd


def main():
    # pd.options.display.max_colwidth = 1000

    survery_df = pd.read_csv("survey.csv")

    # Convert the logs from gcloud's logging to a single dataframe
    logs_df = pd.read_json("logs.json")
    logs_df = logs_df["jsonPayload"]
    logs_df = pd.json_normalize(logs_df)
    logs_df["timestamp"] = pd.to_datetime(logs_df["timestamp"])

    correlated_df = []

    for idx, session_id in enumerate(logs_df.session_id.unique()):
        try:
            logs = logs_df[logs_df.session_id == session_id]

            model_used = logs.query(
                "event == 'processed_collection_images' or event == 'process_collection_images'"
            )["model_name"].iloc[0]

            training_images_length = len(
                logs[logs.request_path == f"/uploads/training_images/{session_id}"]
            )

            start_training_upload = logs.query(
                f"request_path == '/uploads/training_images/{session_id}'"
            )["timestamp"].iloc[0]
            end_training_upload = logs.query(
                "event == 'process_training_images' or event == 'processed_training_images'"
            )["timestamp"].iloc[0]

            training_upload_duration = end_training_upload - start_training_upload

            model_training_duration = logs.query(
                f"request_path == '/uploads/training_images/{session_id}/svm' or request_path == '/uploads/training_images/{session_id}/auto_encoder'"
            )["duration"].iloc[0]

            collection_images_length = len(
                logs[logs.request_path == f"/uploads/collection_images/{session_id}"]
            )

            start_collection_upload = logs.query(
                f"request_path == '/uploads/collection_images/{session_id}'"
            )["timestamp"].iloc[0]
            end_collection_upload = logs.query(
                "event == 'processed_collection_images' or event == 'process_collection_images'"
            )["timestamp"].iloc[0]
            collection_upload_duration = end_collection_upload - start_collection_upload

            model_collection_comparison_duration = logs.query(
                f"request_path == '/uploads/collection_images/{session_id}/svm' or request_path == '/uploads/collection_images/{session_id}/auto_encoder'"
            )["duration"].iloc[0]
        except Exception as e:
            print(f"Error: {e}")
            continue
        else:
            if survery_df[survery_df.session_id == session_id].empty:
                print(f"Session ID: {session_id} not found in survey data")
            else:
                print(f"Session ID: {session_id} found in survey data")

                correlated_df.append(
                    {
                        "session_id": session_id,
                        "model_used": model_used,
                        "training_images_length": training_images_length,
                        "training_upload_duration": training_upload_duration,
                        "model_training_duration": model_training_duration,
                        "collection_images_length": collection_images_length,
                        "collection_upload_duration": collection_upload_duration,
                        "model_collection_comparison_duration": model_collection_comparison_duration,
                    }
                )

    correlated_df = pd.DataFrame(correlated_df)
    print(correlated_df)

    survery_df = pd.merge(
        survery_df, correlated_df, how="inner", on="session_id", validate="one_to_one"
    )

    print(survery_df)
    survery_df.to_csv("correlated_data.csv", index=False)


if __name__ == "__main__":
    main()
