#!/usr/bin/env node

import { config } from "dotenv";
import { resolve } from "path";

// Load environment variables from .env.local
config({ path: resolve(__dirname, "..", ".env.local") });

import { execSync } from "child_process";
import { writeFileSync, mkdirSync, readFileSync } from "fs";
import { join } from "path";

// Read API URL directly from environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const OPENAPI_URL = `${API_BASE_URL}/api/v1/openapi.json`;
const OUTPUT_DIR = join(__dirname, "..", "types");
const OUTPUT_FILE = join(OUTPUT_DIR, "api.ts");

async function generateTypes() {
  try {
    console.log("🚀 Generating TypeScript types from OpenAPI schema...");
    console.log(`📡 Fetching schema from: ${OPENAPI_URL}`);

    // Create types directory if it doesn't exist
    mkdirSync(OUTPUT_DIR, { recursive: true });

    // Generate types using openapi-typescript
    const command = `npx openapi-typescript ${OPENAPI_URL} --output ${OUTPUT_FILE}`;

    console.log(`🔧 Running: ${command}`);
    execSync(command, { stdio: "inherit" });

    console.log("✅ Types generated successfully!");
    console.log(`📁 Output file: ${OUTPUT_FILE}`);

    // Add a header comment to the generated file
    const headerComment = `// This file is auto-generated from OpenAPI schema
// Do not edit manually - regenerate using: npm run generate-types
// Generated from: ${OPENAPI_URL}

`;

    const content = readFileSync(OUTPUT_FILE, "utf-8");
    writeFileSync(OUTPUT_FILE, headerComment + content);
  } catch (error) {
    console.error("❌ Failed to generate types:", error);
    console.log("⚠️  Backend might not be running. Using placeholder types.");
    console.log(
      '💡 Start the backend with "make start-backend" and try again.'
    );

    // Don't exit with error - this allows the build to continue
    // with placeholder types
  }
}

generateTypes();
