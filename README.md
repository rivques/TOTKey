# CPyProjectTemplate
Put a description for your project here!
This repo is a template VS code project for CircuitPython projects that automatically uploads your code to the board when you press F5. Requires F5Anything extension.
## What does this do?
This makes it easier to develop for boards like the Adafruit Metro Express and Raspberry Pi Pico by automatically uploading your code to the board's `code.py`. No more worrying about if your latest changes got saved to Git, or switching to a new board and losing all your libraries!
## Use
### Every new project:
1. Make a GitHub account if you don't have one with your normal school credentials and sign into it.
2. Click the big green Use This Template button at the top of this page.
3. Name the new repository something appropriate to the purpose of your project (Your first one should probably be named `Engr3`).
4. Hit "Create repository from template." (The default settings should be fine.)
5. Open VS Code on your machine. Click Clone Repository. If it doesn't show up, hit Ctrl+Shift+P and then type Clone, then hit Enter.
6. Paste in the link to the new repository you've just created from the template and hit enter.
7. For the location, Documents folder.
8. Hit "Open Cloned Directory" in the bottom-left corner.
9. Install the reccomended extensions when you get that popup in the lower right corner. IF the pop-up dissapears before you can click it, hit the tiny bell icon in the lower left corner to bring it back.
### To commit from VS Code:
1. Go to the little branch icon in the left bar of VS Code.
2. Click the + icon next to the files you want to commit.
3. Write a message that descibes your changes in the "Message" box and hit commit.
4. If you get an error about user.name and user.email, see the next section.
5. Click the "Sync changes" button.
### If you get an error about user.name and user.email
1. In VS Code, hit `` Ctrl+Shift+` ``
2. Filling in your actual information, run the following commands one line at a time. The paste shortcut is `Ctrl+V` or you can right click then hit paste. Spelling must match exactly:
```
git config --global user.name YOURGITHUBUSERNAME
git config --global user.email YOURSCHOOLEMAIL
```
3. Return to the previous section.
### To install a library:
1. Get the library files from the Adafruit bundle (probably a .mpy file or a folder.)
2. Copy them to the lib folder *in your project's folder, usually in Documents.* **Don't copy to the lib folder on the board! It will not work!**
3. Hit F5 and the library will be uplaoded to the board.
