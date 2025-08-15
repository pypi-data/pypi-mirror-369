import os


class DirectoryLoader:
    """
    A class for loading objects from files in a specified directory.
    """

    def __init__(self, constructor):
        """
        Initializes a DirectoryLoader instance.

        Args:
            constructor: A callable that constructs an object from a file.

        Returns:
            None
        """
        self.constructor = constructor
        self.loaded = {}

    def loadFromDirectory(self, directory, filter_function=None):
        """
        Loads files from the specified directory and constructs objects using the provided constructor.

        Args:
            directory (str): The path to the directory from which to load files.
            filter_function (callable, optional): A function to filter files. If None, all files are loaded. Defaults to None.

        Returns:
            None
        """
        files = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        print(files)
        for filename in sorted(files):
            if filter_function is None or filter_function(filename):
                self.loaded[filename] = self.constructor(
                    os.path.join(directory, filename)
                )

    def callFunction(self, function, *args):
        """
        Calls a specified function on all loaded objects with the provided arguments.

        Args:
            function (str): The name of the function to call on each loaded object.
            *args: The arguments to pass to the function.

        Returns:
            None
        """
        for key in self.loaded.keys():
            getattr(self.loaded[key], function)(*args)

    def getList(self):
        """
        Retrieves a list of all loaded objects.

        Returns:
            list: A list of loaded objects.
        """
        return list(self.loaded.values())

    def getKeys(self):
        """
        Retrieves a list of all keys corresponding to the loaded objects.

        Returns:
            list: A list of keys for the loaded objects.
        """
        return list(self.loaded.keys())
