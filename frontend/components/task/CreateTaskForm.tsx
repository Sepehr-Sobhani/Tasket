"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loading } from "@/components/ui/loading";
import { components } from "@/types/api-common";

// Use the auto-generated types from OpenAPI
type Epic = components["schemas"]["Epic"];
type User = components["schemas"]["User"];

interface CreateTaskFormProps {
  projectId: number;
  epics: Epic[];
  users: User[];
  onSubmit: (data: {
    title: string;
    description: string;
    priority: string;
    assignee_id?: number;
    epic_id?: number;
  }) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function CreateTaskForm({
  projectId,
  epics,
  users,
  onSubmit,
  onCancel,
  isLoading = false,
}: CreateTaskFormProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    priority: "medium",
    assignee_id: undefined as number | undefined,
    epic_id: undefined as number | undefined,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.title.trim()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="title">Task Title *</Label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Enter task title"
          required
          disabled={isLoading}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          placeholder="Describe your task"
          rows={3}
          disabled={isLoading}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="priority">Priority</Label>
          <Select
            value={formData.priority}
            onValueChange={(value) =>
              setFormData({ ...formData, priority: value })
            }
            disabled={isLoading}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="z-[60] border-gray-200 rounded-lg shadow-lg bg-white">
              <SelectItem
                value="low"
                className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
              >
                Low
              </SelectItem>
              <SelectItem
                value="medium"
                className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
              >
                Medium
              </SelectItem>
              <SelectItem
                value="high"
                className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
              >
                High
              </SelectItem>
              <SelectItem
                value="urgent"
                className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
              >
                Urgent
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="assignee">Assignee</Label>
          <Select
            value={formData.assignee_id?.toString() || ""}
            onValueChange={(value) =>
              setFormData({
                ...formData,
                assignee_id: value ? parseInt(value) : undefined,
              })
            }
            disabled={isLoading}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select assignee" />
            </SelectTrigger>
            <SelectContent className="z-[60] border-gray-200 rounded-lg shadow-lg bg-white">
              <SelectItem
                value=""
                className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
              >
                Unassigned
              </SelectItem>
              {users.map((user) => (
                <SelectItem
                  key={user.id}
                  value={user.id.toString()}
                  className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
                >
                  {user.full_name || user.username}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {epics.length > 0 && (
        <div className="space-y-2">
          <Label htmlFor="epic">Epic (Optional)</Label>
          <Select
            value={formData.epic_id?.toString() || ""}
            onValueChange={(value) =>
              setFormData({
                ...formData,
                epic_id: value ? parseInt(value) : undefined,
              })
            }
            disabled={isLoading}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select epic" />
            </SelectTrigger>
            <SelectContent className="z-[60] border-gray-200 rounded-lg shadow-lg bg-white">
              <SelectItem
                value=""
                className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
              >
                No Epic
              </SelectItem>
              {epics.map((epic) => (
                <SelectItem
                  key={epic.id}
                  value={epic.id.toString()}
                  className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
                >
                  {epic.title}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="flex justify-end space-x-2 pt-4">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading || !formData.title.trim()}>
          {isLoading ? (
            <>
              <Loading size="sm" className="mr-2" />
              Creating...
            </>
          ) : (
            "Create Task"
          )}
        </Button>
      </div>
    </form>
  );
}
