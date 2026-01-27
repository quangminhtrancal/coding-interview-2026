# Basic operations (APPEND, MOVE, BACKSPACE)
# Selection and clipboard (SELECT, CUT, PASTE)
# History management (UNDO, REDO)
# Multiple documents (CREATE, SWITCH)

from os import name


class TextEditorState:
    def __init__(self, content="", cursor=0, selection_start=0, selection_end=0):
        self.content = content
        self.cursor = cursor
        self.selection_start = selection_start
        self.selection_end = selection_end

    def copy(self):
        return TextEditorState(
            self.content,
            self.cursor,
            self.selection_start,
            self.selection_end
        )
    
class TextEditor:
    def __init__(self, shared_clipboard):
        self.content = ""
        self.cursor = 0
        self.selection_start = 0
        self.selection_end = 0
        self.shared_clipboard = shared_clipboard
        self.history = []
        self.redo_stack = []

    def save_state(self):
        """Save current state for undo"""
        state = TextEditorState(
            self.content,
            self.cursor,
            self.selection_start,
            self.selection_end )
        
        self.history.append(state)
        self.redo_stack.clear()
    
    def append(self, text):
        self.save_state()
        if self.has_selection():
        # Replace selection
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            self.content = self.content[:start] + text + self.content[end:]
            self.cursor = start + len(text)
        else:
        # Insert at cursor
            self.content = self.content[:self.cursor] + text + self.content[self.cursor:]
            self.cursor += len(text)
        
        self.clear_selection()
        return self.content
    
    def move(self, position):
        position = max(0, min(int(position), len(self.content)))
        self.cursor = position
        self.clear_selection()
        return self.content
    
    def backspace(self):
        self.save_state()

        if self.has_selection():
        # Delete selection
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            self.content = self.content[:start] + self.content[end:]
            self.cursor = start
        elif self.cursor > 0:
            # Delete character before cursor
            self.content = self.content[:self.cursor-1] + self.content[self.cursor:]
            self.cursor -= 1
        
        self.clear_selection()
        return self.content
    
    def select(self, start, end):
        start = max(0, min(int(start), len(self.content)))
        end = max(0, min(int(end), len(self.content)))

        self.selection_start = start
        self.selection_end = end
        self.cursor = end

        return self.content
    
    def cut(self):
        if not self.has_selection():
            return self.content
        
        # Copy to clipboard
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)
        self.shared_clipboard.content = self.content[start:end]

        # Delete selection
        return self.backspace()
    
    def paste(self):
        return self.append(self.shared_clipboard.content)
    
    def undo(self):
        if not self.history:
            return self.content
    
        # Save current state to redo stack
        current = TextEditorState(
        self.content,
        self.cursor,
        self.selection_start,
        self.selection_end
        )

        self.redo_stack.append(current)
        
        # Restore previous state
        prev_state = self.history.pop()
        self.content = prev_state.content
        self.cursor = prev_state.cursor
        self.selection_start = prev_state.selection_start
        self.selection_end = prev_state.selection_end

        return self.content
    
    def redo(self):
        if not self.redo_stack:
            return self.content
        
        # Save current state to history
        current = TextEditorState(
        self.content,
        self.cursor,
        self.selection_start,
        self.selection_end
        )
        self.history.append(current)
        
        # Restore redo state
        redo_state = self.redo_stack.pop()
        self.content = redo_state.content
        self.cursor = redo_state.cursor
        self.selection_start = redo_state.selection_start
        self.selection_end = redo_state.selection_end

        return self.content
    
    def has_selection(self):
        return self.selection_start != self.selection_end
    
    def clear_selection(self):
        self.selection_start = 0
        self.selection_end = 0

class SharedClipboard:
    def __init__(self):
        self.content = ""
        
class TextEditorManager:
    def __init__(self):
        self.clipboard = SharedClipboard()
        self.documents = {}
        self.active_document = None
    def create(self, name):
        if name in self.documents:
            return ""
        
        self.documents[name] = TextEditor(self.clipboard)
        return ""
    
    def switch(self, name):
        if name not in self.documents:
            return ""
        self.active_document = name
        return self.documents[name].content
    
    def get_active_editor(self):
        if self.active_document and self.active_document in self.documents:
            return self.documents[self.active_document]
        return None