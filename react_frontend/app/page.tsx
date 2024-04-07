"use client";
import React, { useState } from "react";
import UploadSection from "./components/upload-section";

// Import necessary CSS files
import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";

export default function Home() {
  const trainingEndpoint = "/uploads/training_images";
  const [collectionEndpoint, setCollectionEndpoint] = useState<string>('/uploads/collection_images');
  const [matchingFiles, setMatchingFiles] = useState<File[]>([])

  // function used in child component that will send back matching image files to display
  const sendMatchingFiles = (files: File[]) => {
    const topFiles = files.slice(0, 10)
    setMatchingFiles(topFiles);
  }

  return (
    <main className="flex min-h-screen flex-col justify-between p-24">
      <div className="flex flex-col z-10 justify-between gap-10">
        <h1>Capturing Opportunities: AI-Driven Photo Curation for Wildlife Photographer</h1>
        <div className="flex flex-row gap-5">
          <UploadSection title="Upload Training Images" apiEndpoint={trainingEndpoint} sendMatchingFiles={sendMatchingFiles} setCollectionEndpoint={setCollectionEndpoint} />
          <UploadSection title="Upload Image Collection" apiEndpoint={collectionEndpoint} sendMatchingFiles={sendMatchingFiles} setCollectionEndpoint={setCollectionEndpoint} />
        </div>
        <div className="p-3 bg-white rounded-md">
          <h3>Matching Images</h3>
          <div className="h-60">
            {matchingFiles.length === 0 ? (
              <span>Please upload training and collection images to see your results.</span>
            ) : (
              <div className="flex flex-wrap gap-2 mt-2 overflow-scroll">
                {matchingFiles.map((file, key) => {
                  return (
                    <div key={key} className="overflow-hidden relative">
                      <img onClick={() => { console.log(file) }} className="h-20 w-20 rounded-md" src={URL.createObjectURL(file)} />
                      <span className="text-[12px]">{file.name}</span>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
