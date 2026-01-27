'''
Level 1: Basic file operations (ADD_FILE, GET_FILE_SIZE, MOVE_FILE)
Level 2: Find largest files with prefix matching
Level 3: File versioning support
Level 4: Delete and restore operations


'''
class CloudStorageSystem:
    def __init__(self):
        self.files = {} # filename -> size
        self.file_versions = {} # filename -> [size1, size2, ...]
        self.trash = {} # filename -> [size1, size2, ...]

    def add_file(self, filename, size):
        size = int(size)
        if filename in self.files:
        # File exists, overwrite
            self.files[filename] = size
            return "overwritten"
        else:
        # New file
            self.files[filename] = size
            return "created"
        
    def get_file_size(self, filename):
        if filename in self.files:
            return str(self.files[filename])
        return ""
    
    def move_file(self, old_name, new_name):
        if old_name not in self.files:
            return "false"
        if new_name in self.files:
            return "false" # Destination exists
    
        # Move file
        self.files[new_name] = self.files[old_name]
        del self.files[old_name]
        
        # Handle versioning if applicable
        if old_name in self.file_versions:
            self.file_versions[new_name] = self.file_versions[old_name]
            del self.file_versions[old_name]

        return "true"
    
    def get_largest_n(self, prefix, n):
        n = int(n)
        # Find files matching prefix
        matching_files = []

        for filename, size in self.files.items():
            if filename.startswith(prefix):
                matching_files.append((filename, size))

        if not matching_files:
            return ""
        
        # Sort by size (desc), then by name (asc)
        matching_files.sort(key=lambda x: (-x[1], x[0]))
        # Take top n
        top_files = matching_files[:n]
        result = ", ".join([f"{name}({size})" for name, size in top_files])

        return result
    
    def add_version(self, filename, size):
        """For Level 3: Add version to existing file"""
        size = int(size)
        if filename not in self.files:
            # New file
            self.files[filename] = size
            self.file_versions[filename] = [size]
            return "created"
        else:
            # Add version
            if filename not in self.file_versions:
                self.file_versions[filename] = [self.files[filename]]
                
            self.file_versions[filename].append(size)
            self.files[filename] = size # Update current version
            return "overwritten"
    
    def get_version(self, filename, version):
        """Get specific version of file"""
        version = int(version) - 1 # Convert to 0-based index
        if (filename not in self.file_versions or
            version < 0 or
            version >= len(self.file_versions[filename])):
            return ""
        
        return str(self.file_versions[filename][version])
    
    def delete_files(self, prefix):
        """Level 4: Delete files with given prefix"""
        deleted_count = 0
        to_delete = []
        
        for filename in self.files:
            if filename.startswith(prefix):
                to_delete.append(filename)

        for filename in to_delete:
            # Move to trash
            if filename not in self.trash:
                self.trash[filename] = []
            
            self.trash[filename].append(self.files[filename])

            # Handle versions
            if filename in self.file_versions:
                self.trash[filename].extend(self.file_versions[filename][:-1])
                del self.file_versions[filename]

            del self.files[filename]
            deleted_count += 1
        
        return str(deleted_count)
        
    def restore_files(self, prefix):
        """Level 4: Restore files with given prefix"""
        restored_count = 0
        to_restore = []

        for filename in self.trash:
            if filename.startswith(prefix):
                to_restore.append(filename)
        
        for filename in to_restore:
            if filename not in self.files:
                # Only restore if not exists
                versions = self.trash[filename]
                self.files[filename] = versions[-1]
    
                # Latest version
                if len(versions) > 1:
                    self.file_versions[filename] = versions
                    del self.trash[filename]
                
                    restored_count += 1
        return str(restored_count)