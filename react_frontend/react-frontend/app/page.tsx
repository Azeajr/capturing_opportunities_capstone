"use client";
import React, { useState } from "react";
import Button from "@mui/material/Button";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import styled from "@emotion/styled";

// Import necessary CSS files
import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";

const VisuallyHiddenInput = styled("input")({
  clip: "rect(0 0 0 0)",
  clipPath: "inset(50%)",
  height: 1,
  overflow: "hidden",
  position: "absolute",
  bottom: 0,
  left: 0,
  whiteSpace: "nowrap",
  width: 1,
});

const host = "http://localhost:8000";

const training_endpoint = "/uploads/training_images";
const collection_endpoint = "/uploads/collection_images";

export default function Home() {
  // Use FileList type for the state that will hold the selected files
  const [files, setFiles] = useState<FileList | null>(null);
  // const [csrfToken, setCsrfToken] = useState<string | null>(null);

  // Fetch the CSRF token from the server
  // React.useEffect(() => {
  //   fetch(`${host}/csrf_token`)
  //     .then((response) => response.json())
  //     .then((data) => {
  //       setCsrfToken(data.csrfToken);
  //     });
  // }, []);

  // The event type is React.ChangeEvent<HTMLInputElement> for an input change event
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Check if files are selected and update the state
    if (event.target.files) {
      setFiles(event.target.files);
    }
  };

  // The upload function doesn't directly interact with any DOM events, so it doesn't need a specific event type
  const handleUpload = async (api_endpoint: string) => {
    if (!files) {
      alert("No files selected.");
      return;
    }

    const formData = new FormData();
    // Use Array.from to iterate over the FileList since it's not an actual array
    Array.from(files).forEach((file) => {
      // formData.append(api_endpoint.split("/").at(-1)!, file);
      formData.append("files", file);
    });

    try {
      const response = await fetch(`${host}${api_endpoint}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      // const data = await response.json();
      console.log(response);
      setFiles(null);
      alert("Files uploaded successfully!");
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to upload files.");
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div>
        <Button
          component="label"
          role={undefined}
          variant="contained"
          tabIndex={-1}
          startIcon={<CloudUploadIcon />}
        >
          Training Images
          <input
            type="file"
            hidden
            onChange={handleFileChange}
            accept="image/*"
            multiple
          />
        </Button>
        {files && (
          <Button
            onClick={() => handleUpload(training_endpoint)}
            variant="contained"
            color="primary"
          >
            Submit Files
          </Button>
        )}
      </div>
      <div>
        <Button
          component="label"
          role={undefined}
          variant="contained"
          tabIndex={-1}
          startIcon={<CloudUploadIcon />}
        >
          Collection Images
          <input
            type="file"
            hidden
            onChange={handleFileChange}
            accept="image/*"
            multiple
          />
        </Button>
        {files && (
          <Button
            onClick={() => handleUpload(collection_endpoint)}
            variant="contained"
            color="primary"
          >
            Submit Files
          </Button>
        )}
      </div>
    </main>
  );
}
