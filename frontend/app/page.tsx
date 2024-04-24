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
  const [sessionId, setSessionId] = useState<string>('')
  

  // function used in child component that will send back matching image files to display
  const sendMatchingFiles = (files: File[]) => {
    const topFiles = files.slice(0, 10)
    setMatchingFiles(topFiles);
  }

  const setSesstionId = (sessionId: string) => setSessionId(sessionId)

  return (
    <main className="flex min-h-screen flex-col justify-between p-24">
      <div className="flex flex-col z-10 justify-between gap-10">
        <div className="text-white">
          <h1 className="font-bold">Capturing Opportunities: AI-Driven Photo Curation for Wildlife Photographer</h1>
          <p className="pt-3">
            Please select a model and then upload images to train the model on. Afterwards, please upload a collection of images that the machine-learning model will sort accordingly and display the top 10 matching images.
          </p>
        </div>

        <div className="flex flex-row gap-5">
          <UploadSection title="Upload Training Images" apiEndpoint={trainingEndpoint} sendMatchingFiles={sendMatchingFiles} setCollectionEndpoint={setCollectionEndpoint} setSesstionId={setSesstionId} />
          <UploadSection title="Upload Image Collection" apiEndpoint={collectionEndpoint} sendMatchingFiles={sendMatchingFiles} setCollectionEndpoint={setCollectionEndpoint} setSesstionId={setSesstionId} />
        </div>
        <div className="p-3 bg-white rounded-md">
          <h3>Matching Images</h3>
          <div className="h-60">
            {matchingFiles.length === 0 ? (
              <span>Please upload training and collection images to see your results.</span>
            ) : (
              <div className="flex flex-wrap gap-2 mt-2 h-60">
                {matchingFiles.map((file, key) => {
                  return (
                    <div key={key} className="relative">
                      <img onClick={() => { console.log(file) }} className="h-20 w-20 rounded-md" src={URL.createObjectURL(file)} />
                      <span className="text-[12px]">{file.name}</span>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
        {matchingFiles.length > 0 && (
          <div className="p-3 bg-white rounded-md">
            <h3>Feedback Survey</h3>
            <p className="py-3">
              Please provide feedback on your experience with this application by filling out the survey below.
              If the survey is not appearing below, please use this link: <a href="https://forms.gle/KQiakv5j9Q83frJa7" target="_blank" className="underline">https://forms.gle/KQiakv5j9Q83frJa7</a>
            </p>
            <div className="h-80">
              <iframe src={`https://docs.google.com/forms/d/e/1FAIpQLSeQlnbvsr72qdba-F_VNMYZbczYNbRYFtBLPpf5pYR1h6rm_g/viewform?usp=pp_url&entry.76857979=${sessionId}`} width="100%" height="100%">Loading…</iframe>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
