"use client"

import React, { useState, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Progress } from "@/components/ui/progress"
import { Upload, Info, Users, Activity, Sparkles } from "lucide-react"
import Link from "next/link"

export default function ScenarioBuilder() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [learningOutcomes, setLearningOutcomes] = useState("")
  const [autofillLoading, setAutofillLoading] = useState(false)
  const [autofillError, setAutofillError] = useState<string | null>(null)
  const [autofillResult, setAutofillResult] = useState<any>(null)
  const [autofillStep, setAutofillStep] = useState<string>("")
  const [autofillProgress, setAutofillProgress] = useState(0)
  const [autofillMaxAttempts, setAutofillMaxAttempts] = useState(60)
  const [isDragOver, setIsDragOver] = useState(false)

  // Placeholder handlers for personas and timeline
  const handleAddPersona = () => {}
  const handleAddScene = () => {}

  // Handler to clear the uploaded file and open the file picker
  const handleChooseDifferentFile = (e: React.MouseEvent) => {
    e.preventDefault();
    setUploadedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) setUploadedFile(file)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = Array.from(e.dataTransfer.files)
    const pdfFile = files.find(file => file.type === "application/pdf")
    
    if (pdfFile) {
      setUploadedFile(pdfFile)
      // Clear the file input value to ensure it updates
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    } else {
      alert("Please drop a PDF file")
    }
  }

  const handleAutofill = async () => {
    if (!uploadedFile) return;
    setAutofillLoading(true);
    setAutofillError(null);
    setAutofillResult(null);
    setAutofillStep("Uploading PDF...");
    setAutofillProgress(0);
    
    try {
      // Step 1: Upload PDF and get job ID immediately
      const formData = new FormData();
      formData.append("file", uploadedFile);
      const response = await fetch("http://127.0.0.1:8000/api/parse-pdf/", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error("Failed to upload PDF");
      }
      
      const uploadData = await response.json();
      const jobId = uploadData.job_id;
      
      if (!jobId) {
        throw new Error("No job ID received from LlamaParse");
      }
      
      console.log("PDF uploaded, job ID:", jobId);
      setAutofillStep("Parsing PDF content...");
      setAutofillProgress(10); // Upload complete
      
      // Step 2: Poll for completion status
      let attempts = 0;
      const maxAttempts = 60; // 3 minutes with 3-second intervals
      setAutofillMaxAttempts(maxAttempts);
      
      while (attempts < maxAttempts) {
        attempts++;
        const progressPercent = Math.min(10 + (attempts / maxAttempts) * 80, 90); // 10% to 90%
        setAutofillProgress(progressPercent);
        setAutofillStep(`Parsing PDF content... (${attempts}/${maxAttempts})`);
        
        // Check status
        const statusResponse = await fetch(`http://127.0.0.1:8000/api/parse-pdf/status/${jobId}`);
        if (!statusResponse.ok) {
          throw new Error("Failed to check parsing status");
        }
        
        const statusData = await statusResponse.json();
        console.log(`Attempt ${attempts}: Status = ${statusData.status}`);
        
        if (statusData.status === "SUCCESS" || statusData.status === "COMPLETED") {
          // Get the result
          setAutofillStep("Getting parsed content...");
          setAutofillProgress(95);
          const resultResponse = await fetch(`http://127.0.0.1:8000/api/parse-pdf/result/${jobId}`);
          
          if (!resultResponse.ok) {
            throw new Error("Failed to get parsing result");
          }
          
          const resultData = await resultResponse.json();
          console.log("Parse result:", resultData);
          
          if (resultData.status === "completed") {
            setAutofillStep("Complete!");
            setAutofillProgress(100);
            setAutofillResult(resultData);
            
            // Populate form fields with AI results
            if (resultData.ai_result) {
              const aiData = resultData.ai_result;
              console.log("AI Result:", aiData);
              console.log("AI Result keys:", Object.keys(aiData));
              
              // Set the title
              if (aiData.title) {
                console.log("Setting title:", aiData.title);
                setName(aiData.title);
              } else {
                console.log("No title found in AI result");
              }
              
              // Set the description
              if (aiData.description) {
                console.log("Setting description:", aiData.description);
                setDescription(aiData.description);
              } else {
                console.log("No description found in AI result");
                console.log("Description field value:", aiData.description);
              }
              
              // Set the learning outcomes
              if (aiData.learning_outcomes && Array.isArray(aiData.learning_outcomes)) {
                console.log("Setting learning outcomes:", aiData.learning_outcomes);
                setLearningOutcomes(aiData.learning_outcomes.join('\n'));
              } else {
                console.log("No learning outcomes found in AI result");
              }
            } else {
              console.log("No AI result found in response:", resultData);
              console.log("Full result data:", resultData);
            }
            
            return;
          } else {
            throw new Error(`Failed to get result: ${resultData.error}`);
          }
          
        } else if (statusData.status === "FAILED") {
          throw new Error(`Parsing failed: ${statusData.error || 'Unknown error'}`);
        } else if (statusData.status === "PENDING") {
          // Wait before next attempt
          await new Promise(resolve => setTimeout(resolve, 3000));
          continue;
        } else {
          // Unknown status, wait and continue
          console.log(`Unknown status: ${statusData.status}, waiting...`);
          await new Promise(resolve => setTimeout(resolve, 3000));
          continue;
        }
      }
      
      // Max attempts reached
      throw new Error("Parsing timed out. Please try again.");
      
    } catch (err: any) {
      setAutofillError(err.message || "Unknown error");
      console.error("Autofill error:", err);
    } finally {
      setAutofillLoading(false);
      setAutofillStep("");
      setAutofillProgress(0);
    }
  };



  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col items-center py-10 px-2">
      {/* Left overlay sidebar */}
      <div className="fixed top-0 left-0 h-full w-72 z-50 bg-black shadow-2xl flex flex-col items-start pl-8 pt-8">
        <h1 className="mb-10 text-white text-xl font-bold mb-6">
          Simulation Builder
        </h1>
        <Link href="/dashboard" className="mb-6">
          <button className="bg-white text-black rounded px-4 py-2 font-medium shadow hover:bg-gray-200 transition">Back to Dashboard</button>
              </Link>
        {/* Add sidebar navigation or content here */}
      </div>
      {/* Add left padding to prevent content from being hidden under the sidebar */}
      <div className="w-72 h-0" />
      {/* Top overlay bar */}
      <div className="fixed top-0 left-0 w-full z-40 bg-background shadow-lg flex items-center justify-between h-14 px-8">
        <span className="text-lg font-semibold">Simulation Builder</span>
        <div className="flex gap-4">
          <button className="bg-white text-black rounded px-4 py-2 font-medium shadow hover:bg-gray-200 transition">Save</button>
          <button className="bg-black text-white rounded px-4 py-2 font-medium shadow hover:bg-gray-800 transition">Publish</button>
        </div>
      </div>
      {/* Add top padding to prevent content from being hidden under the bar */}
      <div className="h-14" />
      {/* Main content shifted further right to avoid sidebar overlap */}
      <div className="pl-[26rem] w-full">
        {/* Header and Upload Row */}
        <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 items-start">
          {/* Left: Title and Subtitle */}
          <div className="flex flex-col gap-2">
            <h1 className="text-2xl font-bold">Upload your Business Case Study</h1>
            <p className="text-muted-foreground text-sm">We will analyze the contents and autofill the configuration for you.</p>
          </div>
          {/* Right: Drag and Drop File Upload Box */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 flex flex-col items-center justify-center min-h-[120px] cursor-pointer ${
              isDragOver 
                ? 'border-blue-500 bg-blue-50 scale-105' 
                : uploadedFile && uploadedFile.type === "application/pdf"
                ? 'border-green-500 bg-green-50'
                : 'border-gray-300 bg-card hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploadedFile && uploadedFile.type === "application/pdf" ? (
              <span className="flex flex-col items-center">
                {/* Simple PDF icon using SVG */}
                <svg className="h-10 w-10 mx-auto mb-2 text-red-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M6 2a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6H6z" />
                  <path d="M14 2v6h6" />
                </svg>
                <span className="text-xs text-red-500 font-semibold">PDF attached</span>
              </span>
            ) : (
              <Upload className={`h-10 w-10 mx-auto mb-2 ${isDragOver ? 'text-blue-500' : 'text-muted-foreground'}`} />
            )}
            
            {!(uploadedFile && uploadedFile.type === "application/pdf") && (
              <span className={`font-medium ${isDragOver ? 'text-blue-600' : 'text-muted-foreground'}`}>
                {isDragOver ? (
                  <span>Drop your PDF here</span>
                ) : (
                  <span><span className="underline">Click here</span> to upload your PDF or drag and drop</span>
                )}
              </span>
            )}
            
            <input
              id="file-upload"
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleFileChange}
              ref={fileInputRef}
            />
            
            {uploadedFile && (
              <div className="mt-2 text-primary text-sm font-medium">{uploadedFile.name}</div>
            )}
          </div>
          <div className="flex gap-2 justify-right">

          </div>
          {/* Buttons directly below the upload box, perfectly aligned */}
          {uploadedFile && (
            <div className="flex ml-25 gap-2 justify-right">
              {/* Choose a different file */}
              <label htmlFor="file-upload" className="cursor-pointer m-0">
                <button
                  type="button"
                  onClick={handleChooseDifferentFile}
                  className="bg-white text-black rounded px-4 py-2 font-medium shadow hover:bg-gray-200 transition border border-gray-300 w-full h-full align-middle"
                >
                  Choose a different file
                </button>
              </label>
              {/* Use and autofill */}
              <button
                className="bg-black text-white rounded px-2 py-2 font-medium shadow hover:bg-gray-800 transition border border-black w-1000 h-10 align-middle flex items-center justify-center"
                onClick={handleAutofill}
                disabled={autofillLoading}
              >
                <Sparkles className="mr-2 h-4 w-4 text-white inline" />
                Use and autofill
              </button>
            </div>
          )}
          {/* Show loading progress */}
          {autofillLoading && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-800">{autofillStep}</span>
                <span className="text-xs text-blue-600">{Math.round(autofillProgress)}%</span>
              </div>
              <Progress value={autofillProgress} className="w-full h-2" />
            </div>
          )}
          
          {/* Show error */}
          {autofillError && (
            <div className="mt-4 p-4 bg-red-50 rounded-lg border border-red-200">
              <div className="flex items-center">
                <span className="text-red-600 font-medium">Error:</span>
                <span className="text-red-600 ml-2">{autofillError}</span>
              </div>
            </div>
          )}
          
          {/* Show success message */}
          {autofillResult && autofillStep === "Complete!" && (
            <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center">
                <span className="text-green-600 font-medium">✓ Success!</span>
                <span className="text-green-600 ml-2">PDF content has been mapped to your form fields.</span>
              </div>
            </div>
          )}
        </div>

        {/* Accordions */}
        <div className="w-full max-w-4xl">
          <Accordion type="multiple" className="space-y-6" defaultValue={['info', 'personas', 'timeline']}>
            {/* Information Accordion */}
            <AccordionItem value="info">
              <AccordionTrigger className="flex items-center gap-2 text-lg font-semibold justify-start text-left">
                <Info className="h-5 w-5" />
                Information
                <span className="ml-2 text-muted-foreground text-sm font-normal">The overall description of the simulation. This is the foundation and sense of direction.</span>
              </AccordionTrigger>
              <AccordionContent className="overflow-visible" style={{ overflow: 'visible' }}>
                <div className="space-y-5 pt-4 w-full mx-auto overflow-visible">
                  <div className="overflow-visible focus-within:overflow-visible">
                    <Label htmlFor="name">Name</Label>
                    <Input id="name" value={name} onChange={e => setName(e.target.value)} className="mt-1 w-full box-border p-2" />
                  </div>
                  <div className="overflow-visible focus-within:overflow-visible rounded-none">
                    <Label htmlFor="description">Description/Background</Label>
                    <Textarea 
                      id="description" 
                      value={description} 
                      onChange={e => setDescription(e.target.value)} 
                      className="mt-1 w-full overflow-visible rounded-none z-10 p-2 min-h-[200px] resize-y" 
                      style={{ minHeight: '200px', maxHeight: '400px' }}
                    />
                  </div>
                  <div className="overflow-visible focus-within:overflow-visible">
                    <Label htmlFor="learning-outcomes">Learning Outcomes</Label>
                    <Textarea 
                      id="learning-outcomes" 
                      value={learningOutcomes} 
                      onChange={e => setLearningOutcomes(e.target.value)} 
                      className="mt-1 w-full box-border p-2 min-h-[200px] resize-y" 
                      style={{ minHeight: '200px', maxHeight: '400px' }}
                    />
                  </div>
                            <div>
                    <Label className="block mb-1">Files</Label>
                    <span className="block text-muted-foreground text-xs mb-2">Use this to give more context to the simulation</span>
                    <Button variant="outline">Upload Files</Button>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>

            {/* Personas Accordion */}
            <AccordionItem value="personas">
              <AccordionTrigger className="flex items-center gap-2 text-lg font-semibold justify-start text-left">
                <Users className="h-5 w-5" />
                Personas
                <span className="ml-2 text-muted-foreground text-sm font-normal">The characters the user will interact during the simulation with their own personality and goals.</span>
              </AccordionTrigger>
              <AccordionContent>
                <div className="flex flex-col items-center py-6">
                  <Button onClick={handleAddPersona} variant="outline" className="w-60">Add new persona</Button>
                </div>
              </AccordionContent>
            </AccordionItem>

            {/* Timeline Accordion */}
            <AccordionItem value="timeline">
              <AccordionTrigger className="flex items-center gap-2 text-lg font-semibold justify-start text-left">
                <Activity className="h-5 w-5" />
                Timeline
                <span className="ml-2 text-muted-foreground text-sm font-normal">These are the sequence of events the user needs to solve for during the simulation.</span>
              </AccordionTrigger>
              <AccordionContent>
                <div className="py-4">
                  <p className="text-muted-foreground text-sm mb-6">Think of each segment as a self-contained mini-level in your simulation. Arrange them from top to bottom, this will be the sequence each scene will take place in.</p>
                  <div className="flex flex-col items-center">
                    <Button onClick={handleAddScene} variant="outline" className="w-60">Add new Scene</Button>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </div>
    </div>
  )
}
