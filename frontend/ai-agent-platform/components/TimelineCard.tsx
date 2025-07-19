import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface TimelineEvent {
  title: string;
  goal: string;
  sceneDescription: string;
  successMetric: string;
  timeoutTurns?: number;
}

interface TimelineCardProps {
  event: TimelineEvent;
  onSave?: (event: TimelineEvent) => void;
  onDelete?: () => void;
  editMode?: boolean;
}

export default function TimelineCard({ 
  event, 
  onSave, 
  onDelete, 
  editMode = false 
}: TimelineCardProps) {
  const [editFields, setEditFields] = useState({
    title: event.title,
    goal: event.goal,
    sceneDescription: event.sceneDescription,
    successMetric: event.successMetric,
    timeoutTurns: event.timeoutTurns || 15
  });

  // Sync local state with props when event changes
  useEffect(() => {
    setEditFields({
      title: event.title,
      goal: event.goal,
      sceneDescription: event.sceneDescription,
      successMetric: event.successMetric,
      timeoutTurns: event.timeoutTurns || 15
    });
  }, [event]);

  const handleEditFieldChange = (field: string, value: string | number) => {
    setEditFields(fields => ({ ...fields, [field]: value }));
  };

  const handleSave = () => {
    if (onSave) {
      onSave({
        title: editFields.title,
        goal: editFields.goal,
        sceneDescription: editFields.sceneDescription,
        successMetric: editFields.successMetric,
        timeoutTurns: editFields.timeoutTurns
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
        className="flex flex-row items-stretch w-full max-w-4xl min-h-[140px] p-3 mb-3 border border-gray-200 shadow-md cursor-pointer"
        tabIndex={0}
        aria-label={`Edit timeline event: ${event.title}`}
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
    <div className="w-full max-w-3xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Black Header */}
      <div className="bg-black text-white p-6 rounded-t-lg">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-black" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12,6 12,12 16,14" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold">Scenario Segment</h2>
            <p className="text-sm text-gray-300">Each segment represents a key event or decision point in the simulation. The more descriptive you are, the more realistic your scenario will be.</p>
          </div>
        </div>
      </div>
      
      {/* Content */}
      <div className="grid grid-cols-2 gap-8 p-8">
        {/* Left Column */}
        <div className="flex flex-col space-y-6">
          <div className="flex items-center space-x-4">
            <div className="w-24 h-24 rounded-lg bg-gray-200 overflow-hidden flex items-center justify-center">
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12,6 12,12 16,14" />
              </svg>
            </div>
            <div className="flex-1">
              <span className="block text-gray-700 font-semibold text-lg">Title</span>
              <Input
                id="event-title"
                className="mt-1 block w-full rounded border-gray-300 text-base font-medium"
                value={editFields.title}
                onChange={e => handleEditFieldChange("title", e.target.value)}
                placeholder="Event Title"
              />
              <span className="block text-gray-700 font-semibold mt-3">Goal</span>
              <Input
                id="event-goal"
                className="mt-1 block w-full rounded border-gray-300 text-base"
                value={editFields.goal}
                onChange={e => handleEditFieldChange("goal", e.target.value)}
                placeholder="Goal"
              />
            </div>
          </div>
          <div>
            <span className="block text-xl font-bold text-gray-800 mb-2">Scene Description</span>
            <Textarea
              id="event-description"
              className="w-full bg-gray-50 resize-none min-h-[180px] text-base border border-gray-200 rounded text-gray-700 focus:ring-2 focus:ring-black focus:border-black"
              value={editFields.sceneDescription}
              onChange={e => handleEditFieldChange("sceneDescription", e.target.value)}
              placeholder="Scene Description"
              rows={11}
            />
          </div>
        </div>
        {/* Right Column */}
        <div className="flex flex-col space-y-6">
          <div>
            <span className="block text-xl font-bold text-gray-800 mb-2">Success Metric</span>
            <Textarea
              id="event-success-metric"
              className="w-full bg-gray-50 resize-none min-h-[180px] text-base border border-gray-200 rounded text-gray-700 focus:ring-2 focus:ring-black focus:border-black"
              value={editFields.successMetric}
              onChange={e => handleEditFieldChange("successMetric", e.target.value)}
              placeholder="Success Metric"
              rows={11}
            />
          </div>
          <div>
            <span className="block text-gray-700 font-semibold">Timeout Turns</span>
            <Input
              id="event-timeout"
              type="number"
              className="mt-1 block w-full rounded border-gray-300 text-base"
              value={editFields.timeoutTurns}
              onChange={e => handleEditFieldChange("timeoutTurns", parseInt(e.target.value) || 15)}
              placeholder="15"
              min="1"
              max="100"
            />
          </div>
        </div>
        {/* Action Buttons */}
        <div className="col-span-2 flex justify-end space-x-4 pt-6 border-t border-gray-200">
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
    </div>
  );
} 