"use client";

import { useState } from "react";
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

interface CreateProjectFormProps {
  onSubmit: (data: {
    name: string;
    description: string;
    visibility: string;
  }) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function CreateProjectForm({
  onSubmit,
  onCancel,
  isLoading = false,
}: CreateProjectFormProps) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    visibility: "private",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-3">
        <Label htmlFor="name" className="text-sm font-medium text-gray-700">
          Project Name *
        </Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="Enter project name"
          required
          disabled={isLoading}
          className="border-gray-200 focus:border-primary focus:ring-primary rounded-lg"
        />
      </div>

      <div className="space-y-3">
        <Label
          htmlFor="description"
          className="text-sm font-medium text-gray-700"
        >
          Description
        </Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          placeholder="Describe your project"
          rows={3}
          disabled={isLoading}
          className="border-gray-200 focus:border-primary focus:ring-primary rounded-lg"
        />
      </div>

      <div className="space-y-3">
        <Label
          htmlFor="visibility"
          className="text-sm font-medium text-gray-700"
        >
          Visibility
        </Label>
        <Select
          value={formData.visibility}
          onValueChange={(value) =>
            setFormData({ ...formData, visibility: value })
          }
          disabled={isLoading}
        >
          <SelectTrigger className="border-gray-200 focus:border-primary focus:ring-primary rounded-lg">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="z-[60] border-gray-200 rounded-lg shadow-lg bg-white">
            <SelectItem
              value="private"
              className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
            >
              Private
            </SelectItem>
            <SelectItem
              value="public"
              className="hover:bg-primary/10 focus:bg-primary/10 rounded-md"
            >
              Public
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex justify-end space-x-3 pt-6 border-t border-gray-100">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
          className="border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg"
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isLoading || !formData.name.trim()}
          className="bg-primary hover:bg-primary/90 text-white rounded-lg"
        >
          {isLoading ? (
            <>
              <Loading size="sm" className="mr-2" />
              Creating...
            </>
          ) : (
            "Create Project"
          )}
        </Button>
      </div>
    </form>
  );
}
