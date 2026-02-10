# Facade Pattern

### 1. What is it?

The Facade is a structural design pattern that provides a simplified, high-level interface to a complex subsystem of classes, a library, or a framework. The Facade class hides the complexity of the underlying system and provides the client with a single, unified entry point to perform common tasks. The pattern does not add new functionality but rather simplifies the access to existing functionality.

The book uses the analogy of calling a shop's customer service operator. The operator is a facade to the complex internal system of departments (ordering, payment, delivery). You don't interact with each department directly; you just talk to the operator, who orchestrates the work for you.

### 2. Why it is required?

It is required to reduce complexity and decouple a client from a complex subsystem. When an application needs to interact with a sophisticated library or framework, the client code can become tightly coupled to the implementation details of dozens of classes. This makes the client code hard to understand, write, and maintain. If the underlying subsystem is ever updated or replaced, it requires significant and risky changes throughout the client's business logic.

The Facade pattern solves this by creating an intermediary class that isolates the client from the complex subsystem.

### 3. Details and key points and examples in the reference Book

- **Core Concept:**
    - A Facade is a class that provides a simple interface to a complex subsystem containing many "moving parts."
- **Limited but Focused Interface:**
    - The Facade might provide limited functionality compared to using the subsystem directly. However, it is designed to include only the features that clients *actually care about*, making it much easier to use for common tasks.
- **Key Roles and Structure:**
    - **The Facade:** This class knows how to interact with the complex subsystem. It receives simple requests from the client and delegates them to the appropriate objects within the subsystem.
    - **The Complex Subsystem:** This is the collection of classes, libraries, or frameworks that the Facade is simplifying. These subsystem classes are not aware of the Facade's existence; they operate independently and can be used directly if needed.
    - **The Client:** The client class uses the Facade to interact with the subsystem instead of calling the subsystem's objects directly.
- **Decoupling:**
    - The primary goal is to decouple the client from the subsystem. If the subsystem changes (e.g., a library update), you only need to update the code within the Facade, not in the dozens of places where it might have been used in the client code.
- **Book Example:**
    - The book uses the example of a `VideoConverter` class. A third-party video conversion framework is extremely complex, with classes for different codecs (`OggCompressionCodec`, `MPEG4CompressionCodec`), file readers (`BitrateReader`), and more. The Facade (`VideoConverter`) provides a single, simple `convert()` method that hides all of this complexity.

### 4. When to Use vs. When to Avoid?

- ✅ **When to Use:**
    - Use the Facade pattern when you need a limited but straightforward interface to a complex subsystem. This is its most common and powerful use case.
    - Use it when you want to structure a subsystem into layers. Each layer can have its own Facade as an entry point, which helps reduce coupling between the layers themselves.
    - Use it to wrap a poorly designed or hard-to-use API to make it more friendly and understandable.
- ⚠️ **When to Avoid (Anti-Pattern Warning):**
    - **God Object:** Be careful that the Facade doesn't evolve into a "God Object" that is coupled to every class in the entire application. If a Facade starts accumulating too many unrelated responsibilities, it might be time to split it into multiple, more focused Facades.
    - **Over-engineering:** If the subsystem is already simple and easy to work with, adding a Facade is unnecessary complexity. Don't add a Facade just for the sake of the pattern.

### 5. Step By Step Detailed Rules to Map the concept to C# code

1. **Identify the Complex Subsystem:** First, identify the set of related classes that are complex to work with directly. This could be a third-party library or a feature area within your own application.
2. **Define the Simple Interface:** Think from the client's perspective. What is the one simple task they want to accomplish? Define a new Facade class with a public method that represents this task (e.g., `ConvertVideo(...)`).
3. **Implement the Facade Logic:** Inside the Facade's method, write the complex code required to orchestrate the subsystem classes. This includes instantiating them, calling their methods in the correct sequence, and managing any data flow between them. The Facade holds references to the subsystem objects, but these are typically kept private.
4. **Refactor the Client:** Go to the client code and replace all the complex, direct calls to the subsystem with a single call to the Facade's new, simple method. The client should now only know about the Facade class.

### 6. C# code Example which is not in the correct state

This "Bad Code" demonstrates a client that is tightly coupled to a complex video conversion subsystem, making the client code hard to read and maintain.

```csharp
// BAD CODE: The client is tightly coupled to the complex subsystem.

// --- The Complex Subsystem ---
// (These are the complicated classes from a hypothetical library we don't control)
public class VideoFile { public VideoFile(string filename) { /* ... */ } }
public class OggCompressionCodec { /* ... */ }
public class MPEG4CompressionCodec { /* ... */ }
public static class CodecFactory { public static string Extract(VideoFile file) => "ogg"; }
public static class BitrateReader { public static string Read(string filename, string sourceCodec) => "dummy_buffer"; }
public static class AudioMixer { public string Fix(string result) => "final_result_with_audio"; }
// ... and many more complex classes

// --- The Client ---
public class UploadService
{
    // The client's business logic is polluted with complex subsystem interactions.
    public void UploadVideo(string fileName)
    {
        Console.WriteLine("--- Preparing video for upload ---");
        var file = new VideoFile(fileName);

        // Problem 1: Client has to know about the CodecFactory and its logic.
        var sourceCodec = CodecFactory.Extract(file);

        // Problem 2: Client contains complex logic to decide which format to use.
        object destinationCodec;
        if (sourceCodec == "ogg")
        {
            destinationCodec = new MPEG4CompressionCodec();
            Console.WriteLine("Converting from OGG to MPEG4...");
        }
        else
        {
            destinationCodec = new OggCompressionCodec();
            Console.WriteLine("Converting to OGG...");
        }

        // Problem 3: Client must call methods in a very specific order.
        var buffer = BitrateReader.Read(fileName, sourceCodec);
        // Pretend BitrateReader.Convert exists
        var result = "converted_video_without_audio";

        var finalResult = new AudioMixer().Fix(result);

        Console.WriteLine($"Uploading '{finalResult}' to the cloud.");
        Console.WriteLine("--- Upload complete ---");
    }
}

```

### 7. Applying the rules to make it correct

This "Good Code" introduces a `VideoConversionFacade` that encapsulates all the complexity, leaving the client clean and decoupled.

```csharp
// GOOD CODE: Using the Facade Pattern

// --- The Complex Subsystem (Remains the same) ---
public class VideoFile { public VideoFile(string filename) { /* ... */ } }
public class OggCompressionCodec { /* ... */ }
public class MPEG4CompressionCodec { /* ... */ }
public static class CodecFactory { public static string Extract(VideoFile file) => "ogg"; }
public static class BitrateReader { public static string Read(string filename, string sourceCodec) => "dummy_buffer"; }
public static class AudioMixer { public string Fix(string result) => "final_result_with_audio"; }

// Step 2 & 3: Define and implement the Facade.
// It provides a single, simple method that hides the subsystem's complexity.
public class VideoConversionFacade
{
    public string ConvertVideo(string fileName, string format)
    {
        Console.WriteLine("Facade: Conversion started.");

        // All the complex logic from the "bad" client is now hidden inside the facade.
        var file = new VideoFile(fileName);
        var sourceCodec = CodecFactory.Extract(file);

        object destinationCodec;
        if (format == "mp4")
        {
            destinationCodec = new MPEG4CompressionCodec();
            Console.WriteLine("Facade: Using MPEG4 codec.");
        }
        else
        {
            destinationCodec = new OggCompressionCodec();
            Console.WriteLine("Facade: Using OGG codec.");
        }

        var buffer = BitrateReader.Read(fileName, sourceCodec);
        var result = "converted_video_without_audio"; // Dummy result

        var finalResult = new AudioMixer().Fix(result);

        Console.WriteLine("Facade: Conversion completed.");
        return finalResult;
    }
}

// Step 4: Refactor the Client.
// The client's business logic is now clean and easy to read.
public class UploadService
{
    // The client only depends on the simple Facade class.
    private readonly VideoConversionFacade _converter = new VideoConversionFacade();

    public void UploadVideo(string fileName)
    {
        Console.WriteLine("--- Preparing video for upload ---");

        // The client makes one simple call to the Facade.
        string finalResult = _converter.ConvertVideo(fileName, "mp4");

        Console.WriteLine($"Uploading '{finalResult}' to the cloud.");
        Console.WriteLine("--- Upload complete ---");
    }
}

```