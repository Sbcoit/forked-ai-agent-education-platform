import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

interface Scene {
  id: string;
  title: string;
  description: string;
  personas_involved: string[];
  user_goal: string;
  sequence_order: number;
  image_url?: string;
}

interface SceneCardProps {
  scene: Scene;
  onSave?: (scene: Scene) => void;
  onDelete?: () => void;
  editMode?: boolean;
  allPersonas?: any[]; // List of available personas for selection
}

export default function SceneCard({ 
  scene, 
  onSave, 
  onDelete, 
  editMode = false,
  allPersonas = []
}: SceneCardProps) {
  const [editFields, setEditFields] = useState({
    title: scene.title,
    description: scene.description,
    personas_involved: scene.personas_involved,
    user_goal: scene.user_goal,
    sequence_order: scene.sequence_order
  });

  // Sync local state with props when scene changes
  useEffect(() => {
    setEditFields({
      title: scene.title,
      description: scene.description,
      personas_involved: scene.personas_involved,
      user_goal: scene.user_goal,
      sequence_order: scene.sequence_order
    });
  }, [scene]);

  const handleFieldChange = (field: string, value: any) => {
    setEditFields(fields => ({ ...fields, [field]: value }));
  };

  const handleSave = () => {
    if (onSave) {
      onSave({
        ...scene,
        title: editFields.title,
        description: editFields.description,
        personas_involved: editFields.personas_involved,
        user_goal: editFields.user_goal,
        sequence_order: editFields.sequence_order
      });
    }
  };

  const handleDelete = () => {
    if (onDelete) onDelete();
  };

  // Display mode
  if (!editMode) {
    return (
      <Card className="flex flex-row items-stretch w-full max-w-4xl min-h-[160px] p-4 mb-4 border border-gray-200 shadow-md cursor-pointer">
        {/* Left: Scene Image */}
        <div className="flex flex-col items-center justify-center w-40 mr-6">
          <div className="w-32 h-32 rounded-lg bg-gray-100 overflow-hidden flex items-center justify-center">
            {scene.image_url ? (
              <img 
                src={scene.image_url} 
                alt={scene.title} 
                className="object-cover w-full h-full rounded-lg"
                onError={(e) => {
                  // Fallback to placeholder on image load error
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  target.nextElementSibling?.classList.remove('hidden');
                }}
              />
            ) : null}
            <div className={`w-full h-full flex items-center justify-center ${scene.image_url ? 'hidden' : ''}`}>
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                <path d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
              </svg>
            </div>
          </div>
          <div className="text-center mt-2">
            <Badge variant="outline" className="text-xs">
              Scene {scene.sequence_order}
            </Badge>
          </div>
        </div>

        {/* Middle: Scene Details */}
        <div className="flex-1 flex flex-col justify-between">
          <div>
            <div className="text-xl font-bold leading-tight mb-1">{scene.title}</div>
            <div className="text-sm text-gray-600 mb-3 line-clamp-3">{scene.description}</div>
            
            {/* User Goal */}
            <div className="mb-3">
              <span className="text-xs font-semibold text-blue-800 uppercase tracking-wide">Goal:</span>
              <div className="text-sm text-blue-700 mt-1">{scene.user_goal}</div>
            </div>
            
            {/* Personas Involved */}
            {scene.personas_involved.length > 0 && (
              <div>
                <span className="text-xs font-semibold text-green-800 uppercase tracking-wide">Personas Involved:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {scene.personas_involved.map((persona, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs">
                      {persona}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>
    );
  }

  // Edit mode
  return (
    <div className="w-full max-w-4xl mx-auto grid grid-cols-2 gap-8 p-8 bg-white rounded-lg shadow-lg">
      {/* Left Column */}
      <div className="flex flex-col space-y-6">
        {/* Scene Image */}
        <div className="flex flex-col items-center">
          <div className="w-48 h-32 rounded-lg bg-gray-100 overflow-hidden flex items-center justify-center mb-2">
            {scene.image_url ? (
              <img 
                src={scene.image_url} 
                alt={editFields.title} 
                className="object-cover w-full h-full rounded-lg"
              />
            ) : (
              <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                <path d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
              </svg>
            )}
          </div>
          <Badge variant="outline">Scene {editFields.sequence_order}</Badge>
        </div>

        {/* Title and Order */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">Scene Title</label>
            <Input
              value={editFields.title}
              onChange={e => handleFieldChange("title", e.target.value)}
              placeholder="Scene title"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">Sequence Order</label>
            <Input
              type="number"
              min="1"
              value={editFields.sequence_order}
              onChange={e => handleFieldChange("sequence_order", parseInt(e.target.value) || 1)}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Right Column */}
      <div className="flex flex-col space-y-6">
        {/* Description */}
        <div>
          <label className="block text-sm font-semibold text-gray-800 mb-1">Scene Description</label>
          <Textarea
            value={editFields.description}
            onChange={e => handleFieldChange("description", e.target.value)}
            placeholder="Describe the setting, environment, and context of this scene..."
            className="w-full min-h-[100px] resize-none"
            rows={4}
          />
        </div>

        {/* User Goal */}
        <div>
          <label className="block text-sm font-semibold text-gray-800 mb-1">User Goal</label>
          <Textarea
            value={editFields.user_goal}
            onChange={e => handleFieldChange("user_goal", e.target.value)}
            placeholder="What specific objective must the student achieve in this scene?"
            className="w-full min-h-[80px] resize-none"
            rows={3}
          />
        </div>

        {/* Personas Involved */}
        <div>
          <label className="block text-sm font-semibold text-gray-800 mb-1">Personas Involved</label>
          <div className="text-xs text-gray-600 mb-2">Select personas that participate in this scene</div>
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-2 border rounded">
            {allPersonas.map((persona, idx) => {
              const isSelected = editFields.personas_involved.includes(persona.name);
              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    const current = editFields.personas_involved;
                    if (isSelected) {
                      handleFieldChange("personas_involved", current.filter(p => p !== persona.name));
                    } else {
                      handleFieldChange("personas_involved", [...current, persona.name]);
                    }
                  }}
                  className={`px-2 py-1 text-xs rounded transition-colors ${
                    isSelected 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {persona.name}
                </button>
              );
            })}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4">
          <Button 
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700" 
            size="sm" 
            variant="destructive" 
            onClick={handleDelete}
          >
            Delete
          </Button>
          <Button 
            className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800" 
            size="sm" 
            variant="default" 
            onClick={handleSave}
          >
            Save
          </Button>
        </div>
      </div>
    </div>
  );
} 