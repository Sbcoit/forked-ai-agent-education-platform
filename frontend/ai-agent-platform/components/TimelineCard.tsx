import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export interface TimelineEvent {
  id: string;
  title: string;
  goal: string;
  sceneDescription: string;
  successMetric: string;
  timeoutTurns?: number;
}

interface EditFields {
  title: string;
  goal: string;
  sceneDescription: string;
  successMetric: string;
  timeoutTurns: string;
}

interface TimelineCardProps {
  event: TimelineEvent;
  onSave?: (event: TimelineEvent) => void;
  onDelete?: () => void;
  editMode?: boolean;
  draggable?: boolean;
  onDragStart?: (e: React.DragEvent) => void;
  onDragEnd?: (e: React.DragEvent) => void;
  isDragged?: boolean;
}

export default function TimelineCard({ 
  event, 
  onSave, 
  onDelete, 
  editMode = false,
  draggable = false,
  onDragStart,
  onDragEnd,
  isDragged = false
}: TimelineCardProps) {
  const [editFields, setEditFields] = useState<EditFields>({
    title: "",
    goal: "",
    sceneDescription: "",
    successMetric: "",
    timeoutTurns: ""
  });

  // Sync local state with props when event changes
  useEffect(() => {
    setEditFields({
      title: event.title || "New Scene",
      goal: event.goal || "Core challenge for this scene.",
      sceneDescription: event.sceneDescription || "Description of what happens in this scene.",
      successMetric: event.successMetric || "How to measure success in this scene.",
      timeoutTurns: event.timeoutTurns ? event.timeoutTurns.toString() : ""
    });
  }, [event]);

  const handleEditFieldChange = (field: string, value: string | number) => {
    setEditFields(fields => ({ ...fields, [field]: value }));
  };

  const handleTimeoutChange = (value: string) => {
    setEditFields(fields => ({ ...fields, timeoutTurns: value }));
  };

  const handleSave = () => {
    if (onSave) {
      onSave({
        id: event.id,
        title: editFields.title,
        goal: editFields.goal,
        sceneDescription: editFields.sceneDescription,
        successMetric: editFields.successMetric,
        timeoutTurns: editFields.timeoutTurns ? parseInt(editFields.timeoutTurns) || 15 : 15
      });
    }
  };

  const handleDelete = () => {
    if (onDelete) onDelete();
  };

  // Display mode
  if (!editMode) {
    return (
      <Card
        className={`flex flex-row items-stretch w-full max-w-4xl min-h-[140px] p-3 mb-3 border border-gray-200 shadow-md cursor-pointer transition-all duration-200 ${
          isDragged ? 'opacity-50 scale-95' : ''
        }`}
        tabIndex={0}
        aria-label={`Edit timeline event: ${event.title}`}
        draggable={draggable}
        onDragStart={onDragStart}
        onDragEnd={onDragEnd}
      >
        {/* Left: Icon and Info */}
        <div className="flex flex-col items-center justify-center w-32 mr-4">
          <div className="w-16 h-16 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center mb-1">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12,6 12,12 16,14" />
            </svg>
          </div>
        </div>
        {/* Middle: Title, Goal, Description */}
        <div className="flex-1 flex flex-col justify-center pr-6">
          <div className="text-xl font-bold leading-tight mb-0.5">{event.title}</div>
          <div className="text-base text-gray-500 mb-2">{event.goal}</div>
          <div className="text-sm text-gray-800 mb-1">{event.sceneDescription}</div>
          {event.successMetric && (
            <div className="text-xs text-blue-800 mt-1">
              <span className="font-semibold">Success Metric:</span> {event.successMetric}
            </div>
          )}
        </div>
        {/* Right: Timeout Turns */}
        <div className="flex flex-col justify-center min-w-[120px]">
          <div className="text-center">
            <div className="text-sm font-medium text-gray-800">Timeout</div>
            <div className="text-lg font-bold text-gray-600">{event.timeoutTurns || 15} turns</div>
          </div>
        </div>
      </Card>
    );
  }

  // Edit mode (no Card wrapper)
  return (
    <div className="w-full bg-white rounded-lg shadow-lg flex flex-col h-full">
      {/* Black Header */}
      <div className="bg-black text-white p-4 rounded-t-lg flex-shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-black" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12,6 12,12 16,14" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold">Scenario Segment</h2>
            <p className="text-sm text-gray-300">Each segment represents a key event or decision point in the simulation.</p>
          </div>
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-1 p-6">
        <div className="grid grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="col-span-3 flex flex-col space-y-4">
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <span className="block text-gray-700 font-semibold text-sm">Scenario Title</span>
                <Input
                  id="event-title"
                  className="mt-1 block w-full rounded border-gray-300 text-sm font-medium"
                  value={editFields.title}
                  onChange={e => handleEditFieldChange("title", e.target.value)}
                  placeholder="New Scene"
                />
                <span className="block text-gray-700 font-semibold mt-2 text-sm">Goal</span>
                <Input
                  id="event-goal"
                  className="mt-1 block w-full rounded border-gray-300 text-sm"
                  value={editFields.goal}
                  onChange={e => handleEditFieldChange("goal", e.target.value)}
                  placeholder="Core challenge for this scene."
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-6">
              <div className="col-span-2">
                <span className="block text-lg font-bold text-gray-800 mb-2">Scene Description</span>
                <Textarea
                  id="event-description"
                  className="w-full bg-gray-50 resize-none min-h-[200px] text-sm border border-gray-200 rounded text-gray-700 focus:ring-2 focus:ring-black focus:border-black"
                  value={editFields.sceneDescription}
                  onChange={e => handleEditFieldChange("sceneDescription", e.target.value)}
                  placeholder="Description of what happens in this scene."
                  rows={10}
                />
              </div>
              <div className="flex flex-col space-y-4">
                <div>
                  <span className="block text-lg font-bold text-gray-800 mb-2">Success Metric</span>
                  <Textarea
                    id="event-success-metric"
                    className="w-full bg-gray-50 resize-none min-h-[120px] text-sm border border-gray-200 rounded text-gray-700 focus:ring-2 focus:ring-black focus:border-black"
                    value={editFields.successMetric}
                    onChange={e => handleEditFieldChange("successMetric", e.target.value)}
                    placeholder="How to measure success in this scene."
                    rows={6}
                  />
                </div>
                <div>
                  <span className="block text-gray-700 font-semibold text-sm">Timeout Turns</span>
                                <Input
                id="event-timeout"
                type="number"
                className="mt-1 block w-full rounded border-gray-300 text-sm"
                value={editFields.timeoutTurns}
                onChange={e => handleTimeoutChange(e.target.value)}
                placeholder="Turns before the scenario ends."
                min="1"
                max="100"
              />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Action Buttons - Fixed at bottom */}
      <div className="flex justify-end space-x-4 p-4 border-t border-gray-200 bg-gray-50 rounded-b-lg flex-shrink-0">
        <Button 
          id="event-delete-button"
          variant="outline"
          className="px-4 py-2 text-red-600 border-red-300 hover:bg-red-50"
          onClick={handleDelete}
        >
          Delete
        </Button>
        <Button 
          id="event-save-button"
          className="px-4 py-2 bg-black text-white hover:bg-gray-800"
          onClick={handleSave}
        >
          Save
        </Button>
      </div>
    </div>
  );
} 