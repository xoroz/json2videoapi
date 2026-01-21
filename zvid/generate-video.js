import renderVideo from "zvid";
import fs from "fs";
import path from "path";

// Get arguments: node generate-video.js <project-json-path> <output-dir>
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error("Usage: node generate-video.js <project-json-path> <output-dir>");
    process.exit(1);
}

const projectJsonPath = args[0];
const outputDir = args[1];

async function generate() {
    try {
        const projectData = fs.readFileSync(projectJsonPath, "utf-8");
        const project = JSON.parse(projectData);
        console.log("DEBUG: Parsed project:", JSON.stringify(project, null, 2));

        console.log(`Starting video generation for project: ${project.name}`);

        // Ensure output directory exists (zvid might do this, but safe to check)
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        await renderVideo(project, outputDir, (progress) => {
            // Print progress in a format we can parse easily if needed
            console.log(`PROGRESS:${Math.round(progress)}`);
        });

        const outputPath = path.join(outputDir, `${project.name}.mp4`);
        console.log(`SUCCESS:${outputPath}`);

    } catch (error) {
        console.error(`ERROR:${error.message}`);
        process.exit(1);
    }
}

generate();
