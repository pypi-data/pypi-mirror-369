import os, glob, json
import inspect

encodeJSON = json.JSONEncoder().encode
decodeJSON = json.JSONDecoder().decode

class Path:
    join          = os.path.join
    directoryName = os.path.dirname

    @staticmethod
    def exists(path:str) -> bool:
        'check if `path` exists. returns True/False'
        return os.path.exists(path)

    @staticmethod
    def isDirectory(path:str) -> bool:
        return os.path.isdir(path)

    @staticmethod
    def isFile(path:str) -> bool:
        return os.path.isfile(path)

    @staticmethod
    def createDirectory(path:str) -> dict[str,bool|str]:
        '''
        attempt to create a directory provided in `path`. 
        Args:
            path(str): the path to create

        Note:
            if any intermediate directories dont exist, they will be created as well

        Returns:
            the standard dict in the form
            ```
            {
                'status': bool, 
                'log': str
            }
            ```
        '''
        reply = {'status':False, 'log':''}
        if os.system(f"mkdir -p '{path}' 2> /dev/null"):
            reply['log'] = 'failed to create directory. please review your permissions'
            return reply
        
        reply['status'] = True
        return reply
    
    @staticmethod
    def createShortcut(source:str, destination:str) -> dict[str,bool|str]:
        '''
        attempt to create a shortcut.
        Args:
            source(str): the path we want to create a shortcut to
            destination(str): the path to the shortcut 

        Returns:
            the standard dict in the form of
            ```
            {
                'status': bool, 
                'log': str
            }
            ```
        '''
        reply = {'status':False, 'log':''}

        if not Path.exists(source):
            reply['log'] = 'the source path does not exist'
            return reply

        if Path.exists(destination):
            reply['log'] = 'the destination path already exists'
            return reply

        if os.system(f"ln -s -T '{source}' '{destination}' 2> /dev/null"):
            reply['log'] = 'failed to create the shortcut. please confirm that all necessary paths are valid and exist'
            return reply
        
        reply['status'] = True
        return reply

    @staticmethod
    def delete(path:str) -> dict[str,bool|str]:
        '''
        attempt to delete `path`.

        Note:
            if the path is a directory, it will NOT be deleted if its empty 

        Returns:
            the standard dict in the form
            ```
            {
                'status': bool, 
                'log': str
            }
            ```
        '''
        reply = {'status':False, 'log':''}

        if not Path.exists(path):
            reply['log'] = 'path does not exist'
            return reply

        if Path.isDirectory(path) and os.listdir(path):
            reply['log'] = 'can not delete a non-empty directory'
            return reply

        if Path.isFile(path):
            if os.system(f"rm '{path}' 2> /dev/null"):
                reply['log'] = 'failed to delete the file. please ensure you have the right permissions'
                return reply
        else:
            if os.system(f"rmdir '{path}' 2> /dev/null"):
                reply['log'] = 'failed to delete the directory. please ensure you have the right permissions'
                return reply
        
        reply['status'] = True
        return reply

    @staticmethod
    def copy(source:str, destination:str) -> dict[str,bool|str]:
        '''
        attempt to copy a file/directory
        Args:
            source(str): the path we want to copy
            destination(str): the path to the new copy of the file/directory 

        Returns:
            the standard dict in the form
            ```
            {
                'status': bool, 
                'log': str
            }
            ```
        '''
        reply = {'status':False, 'log':''}

        if not Path.exists(source):
            reply['log'] = 'the source path does not exist'
            return reply

        if Path.exists(destination):
            reply['log'] = 'the destination path already exists'
            return reply

        if os.system(f"cp -rfHpu '{source}' '{destination}' 2> /dev/null"):
            reply['log'] = 'failed to copy the source. please confirm that all necessary paths are valid and exist'
            return reply
        
        reply['status'] = True
        return reply

    @staticmethod
    def listDirectory(path:str) -> dict[str,bool|str|list[str]]:
        '''
        attempt to list the contents of a directory
        Args:
            path(str): the path to the directory we want to list

        Returns:
            the standard dict in the form
            ```
            {
                'status': bool, 
                'log': str,
                'contents': list[str] # list of ABSOLUTE paths
            }
            ```
        '''
        reply = {'status':False, 'log':'', 'contents':[]}

        if not Path.isDirectory(path):
            reply['log'] = 'the path given is not a directory'
            return reply

        path += '/*'
        contents = [os.path.abspath(f) for f in glob.glob(path)]

        reply['contents'] = contents
        reply['status'] = True
        return reply

    @staticmethod
    def getMyAbsolutePath() -> str:
        '''
        return the absolute path to the file where this function is called

        Examples:
            if called from:
            * /a/b/c/d/file.py, it will return '/a/b/c/d/file.py'

            * ~/file.py, it will return '/home/{user}/file.py'
        '''
        # Get the frame of the calling function
        caller_frame = inspect.currentframe().f_back

        # Get the file path from the frame
        caller_file = inspect.getframeinfo(caller_frame).filename

        # Return the absolute path of the caller file
        return os.path.abspath(caller_file)

    @staticmethod
    def directoryBackAt(path:str, howFarBack:int=0) -> dict[str,bool|str]:
        '''
        get directory thats `howFarBack` steps from `path`
        Args:
            path(str): path to origin file/directory from where to navigate backwards
            howFarBack(int): how far back to go from the origin `path`. 0 refers the the directory containing the path

        Examples:
            consider:
            ```
            `path` = '/a/b/c/d/e/f/x.png'
            if `howFarBack` = 0, then final directory = '/a/b/c/d/e/f'

            if `howFarBack` = 1, then final directory = '/a/b/c/d/e'
            
            if `howFarBack` = 4, then final directory = '/a/b'
            ```
                    
        Returns:
            dict in form
            ```
            {
                'status': bool,
                'log': str,
                'directory': str
            }
            ```
        '''
        reply = {'status':False, 'log':'', 'directory':''}

        if not Path.exists(path):
            reply['log'] = 'could not find the given path'
            return reply

        if howFarBack<0:
            reply['log'] = 'invalid value given for `howFarBack`'
            return reply

        parent = os.path.dirname(path)

        if howFarBack >= parent.count('/'):
            reply['log'] = 'value of `howFarBack` goes beyond the root directory `/`'
            return reply

        reply['directory'] = '/'.join(parent.split('/')[:-howFarBack]) if howFarBack else parent
        reply['status'] = True
        return reply

if __name__=='__main__':
    pass