## **Mastering the Future: A Deep Dive into Flet 0.7.0's Major Shifts and Service-Oriented Architecture**

I recently used Flet to build an application capable of supporting real-time interpretation. Here are a couple of comparison clips with Apple AirPods, take a look at the results:
<iframe src="//player.bilibili.com/player.html?isOutside=true&aid=115202381121864&bvid=BV1ekpFzPErU&cid=32379767123&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>

<iframe src="//player.bilibili.com/player.html?bvid=BV14zp2zQErg&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

This app uses the Flet framework for multi-platform support. Flet, a project aimed at enabling developers to easily build multi-platform applications with Python, has undergone what can be called a milestone update in its latest **0.7.0.dev** pre-release version.
A friend recently specifically requested file upload/download functionality, so I took the opportunity to upgrade to the 0.7.0.dev version. This update isn't just a simple pile of new features; it's a rethinking of the framework's core architecture, bringing the concept of **"Services"** to the forefront, significantly enhancing application stability and the development experience.

Today, I will take you on a deep dive into this update and share how to configure your environment correctly from the start, as well as how to gracefully migrate your code to the new asynchronous paradigm.

### **I. Forward-Looking Configuration: Pinpointing the Exact Pre-Release Version**

To experience the most cutting-edge features, you need to pinpoint the version accurately. I highly recommend using Poetry for dependency management, as it handles pre-release versions perfectly. In the directory containing your `pyproject.toml`, execute the following commands to build a fully reproducible development environment:

```bash
# Add the precise dev versions of the main library and the audio recorder extension
poetry add "flet[all]==0.70.0.dev5623" --allow-prereleases
poetry add "flet-audio-recorder==0.2.0.dev504" --allow-prereleases
```

For CI/CD environments (like GitHub Actions), your installation steps should be adjusted accordingly:

```yaml
- name: Install dependencies
  run: |
    pip install --pre 'flet[all]==0.70.0.dev5623'
```

### **II. Core Change: Understanding the "Service-Oriented" Architecture**

The most central concept of this update is the introduction of **"Services"**. What is a service? You can think of it as a **persistent, non-visual controller**. Its biggest advantage is that it can "survive" outside the lifecycle of a page (`Page`).

This means:
- **Stronger Stability**: Services won't be accidentally destroyed due to page refreshes, navigation, or updates.
- **Better State Management**: Features that need to run continuously in the background (like audio playback, geolocation) now have a more reliable carrier.
- **Clear Separat
**Separation of Concerns**: UI controls are responsible for display, service controls are responsible for logic and state, resulting in a clearer architecture.

Many familiar functionalities have been re-implemented as services. This is a **Breaking Change** and includes:
`Audio`, `AudioRecorder`, `FilePicker`, `Flashlight`, `Geolocator`, `HapticFeedback`, `InterstitialAd`, `PermissionHandler`, `SemanticsService`, `ShakeDetector`, and others.

**How to use services?**
Before using any service, you must add it to the page's `services` collection, a new property at the same level as the `controls` collection.

```python
import flet as ft

def main(page: ft.Page):
    # Add required services during page initialization
    file_picker = ft.FilePicker()
    page.services.append(file_picker) # Must be added!
    
    page.add(
        ft.ElevatedButton("Pick files", on_click=lambda e: pick_files())
    )
    
    async def pick_files():
        # New API calling method...
        pass
```

### **III. Practical Migration: From Event Callbacks to Elegant Asynchrony**

Let's see the improvement in code elegance brought by the new paradigm through two of the most commonly used modules.

#### **1. FilePicker: Farewell to Cumbersome Event Listening**

**Old Pattern (Event-Driven):**
Previously, using `FilePicker` required defining event handler functions and waiting for the `on_result` event to be triggered. The whole process was asynchronous and non-linear.

```python
def main(page: ft.Page):
    def on_file_picker_result(e: ft.FilePickerResultEvent):
        print("Selected files:", e.files)
    
    file_picker = ft.FilePicker(on_result=on_file_picker_result)
    page.overlay.append(file_picker) # Added to overlay in the old version
    
    def pick_click(e):
        file_picker.pick_files(allow_multiple=True)
    
    page.add(ft.ElevatedButton("Pick files", on_click=pick_click))
```

**New Pattern (Async/Await):**
Now, the API provides direct `async` methods that return results immediately. The code becomes linear and intuitive, almost as if writing synchronous code, greatly improving readability and maintainability.

```python
import flet as ft

async def main(page: ft.Page):
    file_picker = ft.FilePicker()
    page.services.append(file_picker) # Added to services in the new version
    
    async def pick_click(e):
        # One line of code, get the result directly!
        selected_files: list[ft.FilePickerFile] = await file_picker.pick_files_async(allow_multiple=True)
        if selected_files:
            for f in selected_files:
                print(f.name, f.path)
        else:
            print("Cancelled!")
    
    page.add(ft.ElevatedButton("Pick files", on_click=pick_click))
```
The usage of `save_file_async()` and `get_directory_path_async()` is exactly the same.

#### **2. flet-audio-recorder: More Intuitive Audio Control**

The audio recorder extension has also followed the core framework's lead and undergone modernization.

**Old Code (Method
**Old Code (Blocking calls without waiting):**
```python
def handle_start_recording(self, e):
    """Handle starting recording"""
    self.sound_manager.start_recording() # Could not easily wait for completion or handle errors
```

**New Code (Clear asynchronous control):**
```python
async def handle_start_recording(self, e):
    """Handle starting recording"""
    try:
        await self.sound_manager.start_recording() # Async wait, clear flow
        # Logic after recording starts
    except Exception as error:
        # Graceful error handling
        print(f"Recording failed: {error}")
```
This change makes managing the recording lifecycle (start, stop, error handling) incredibly simple and reliable.

### **IV. Summary and Outlook**

The changes in Flet 0.7.0 are far more than simple API adjustments. They mark Flet's evolution from an "advanced UI wrapper library" towards a mature application framework with a **solid, stable underlying architecture**.

- **For Developers**: The comprehensive introduction of `async/await` syntax makes code for complex asynchronous operations concise and elegant, reducing the "callback hell" caused by nested callbacks. It is undoubtedly a huge leap forward in the development experience.
- **For Applications**: The service-oriented architecture solves the core pain point of state persistence, laying a solid foundation for developing more complex and stable applications. It fills us with confidence in using Flet in production environments.

This update requires some learning and migration effort from developers, but I believe it's completely worth it. It represents the framework's evolution aligning with modern Python development best practices.

As a DevRel, I am incredibly excited about this. I firmly believe that deeply understanding and率先 (taking the lead in) applying these changes will not only allow us to build better products but also shape our personal brands as **insightful observers of the technological frontier and reliable problem solvers**.

Let's embrace the change and master the future together.

> **About the Author**: SamYuan, open-source enthusiast, focused on helping developers unlock technical potential and build outstanding products. Feel free to follow me on [Github](https://github.com/SamYuan1990) for more in-depth technical content.
> **PR Address for this Article** [link](https://github.com/SamYuan1990/i18n-agent-action/pull/118)
> **Homepage for this article's project** [link](https://github.com/SamYuan1990/i18n-agent-action)