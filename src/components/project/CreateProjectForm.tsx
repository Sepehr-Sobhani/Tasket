"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Loading } from "@/components/ui/loading";
import {
  projectCreateSchema,
  type ProjectCreateInput,
} from "@/lib/validations/project";

interface CreateProjectFormProps {
  // eslint-disable-next-line no-unused-vars
  onSubmit: (data: ProjectCreateInput) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function CreateProjectForm({
  onSubmit,
  onCancel,
  isLoading = false,
}: CreateProjectFormProps) {
  const form = useForm({
    resolver: zodResolver(projectCreateSchema),
    defaultValues: {
      name: "",
      description: "",
      visibility: "private" as const,
    },
  });

  const handleSubmit = (data: ProjectCreateInput) => {
    onSubmit(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm font-medium text-foreground">
                Project Name *
              </FormLabel>
              <FormControl>
                <Input
                  placeholder="Enter project name"
                  disabled={isLoading}
                  className="border-border focus:border-primary focus:ring-primary rounded-lg"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm font-medium text-foreground">
                Description
              </FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Describe your project"
                  rows={3}
                  disabled={isLoading}
                  className="border-border focus:border-primary focus:ring-primary rounded-lg"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="visibility"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm font-medium text-foreground">
                Visibility
              </FormLabel>
              <Select
                onValueChange={field.onChange}
                defaultValue={field.value}
                disabled={isLoading}
              >
                <FormControl>
                  <SelectTrigger className="border-border focus:border-primary focus:ring-primary rounded-lg">
                    <SelectValue />
                  </SelectTrigger>
                </FormControl>
                <SelectContent className="z-60 border-border rounded-lg shadow-lg bg-popover">
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
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end space-x-3 pt-6 border-t border-border">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
            className="border-border text-muted-foreground hover:bg-muted rounded-lg"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isLoading}
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
    </Form>
  );
}
