"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loading } from "@/components/ui/loading";
import { Badge } from "@/components/ui/badge";
import { X, Plus, Palette } from "lucide-react";
import { api } from "@/lib/api-client";

interface Tag {
  id: number;
  name: string;
  color: string;
  project_id: number;
}

interface TagManagerProps {
  projectId: number;
  tags: Tag[];
  onTagCreated: (tag: Tag) => void;
  onTagDeleted: (tagId: number) => void;
}

const PRESET_COLORS = [
  "#EF4444",
  "#F97316",
  "#F59E0B",
  "#EAB308",
  "#84CC16",
  "#22C55E",
  "#10B981",
  "#14B8A6",
  "#06B6D4",
  "#3B82F6",
  "#6366F1",
  "#8B5CF6",
  "#A855F7",
  "#EC4899",
  "#F43F5E",
];

export function TagManager({
  projectId,
  tags,
  onTagCreated,
  onTagDeleted,
}: TagManagerProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const [selectedColor, setSelectedColor] = useState(PRESET_COLORS[0]);
  const [isLoading, setIsLoading] = useState(false);

  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;

    setIsLoading(true);
    try {
      const response = await api.tags.create({
        name: newTagName.trim(),
        color: selectedColor,
        project_id: projectId,
      });

      if (response) {
        onTagCreated(response);
        setNewTagName("");
        setSelectedColor(PRESET_COLORS[0]);
        setIsCreating(false);
      } else {
        console.error("Failed to create tag");
      }
    } catch (error) {
      console.error("Error creating tag:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTag = async (tagId: number) => {
    setIsLoading(true);
    try {
      await api.tags.delete(tagId);
      onTagDeleted(tagId);
    } catch (error) {
      console.error("Error deleting tag:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Tags</h3>
        <Button
          size="sm"
          onClick={() => setIsCreating(true)}
          disabled={isLoading}
          className="flex items-center bg-accent hover:bg-accent/90 text-accent-foreground"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Tag
        </Button>
      </div>

      {/* Create Tag Form */}
      {isCreating && (
        <div className="p-4 border rounded-lg bg-muted/50">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="tagName">Tag Name</Label>
              <Input
                id="tagName"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                placeholder="Enter tag name"
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label>Color</Label>
              <div className="flex flex-wrap gap-2">
                {PRESET_COLORS.map((color) => (
                  <button
                    key={color}
                    type="button"
                    className={`w-8 h-8 rounded-full border-2 transition-all ${
                      selectedColor === color
                        ? "border-gray-800 scale-110"
                        : "border-gray-300 hover:scale-105"
                    }`}
                    style={{ backgroundColor: color }}
                    onClick={() => setSelectedColor(color)}
                    disabled={isLoading}
                  />
                ))}
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  setIsCreating(false);
                  setNewTagName("");
                  setSelectedColor(PRESET_COLORS[0]);
                }}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleCreateTag}
                disabled={isLoading || !newTagName.trim()}
              >
                {isLoading ? (
                  <>
                    <Loading size="sm" className="mr-2" />
                    Creating...
                  </>
                ) : (
                  "Create Tag"
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Tags List */}
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <Badge
            key={tag.id}
            className="flex items-center space-x-1 px-3 py-1"
            style={{ backgroundColor: tag.color, color: "white" }}
          >
            <span>{tag.name}</span>
            <button
              type="button"
              onClick={() => handleDeleteTag(tag.id)}
              disabled={isLoading}
              className="ml-1 hover:bg-black/20 rounded-full p-0.5"
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}
        {tags.length === 0 && (
          <p className="text-sm text-gray-500">No tags created yet</p>
        )}
      </div>
    </div>
  );
}
