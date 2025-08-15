emptymsg = 'Write something'
msgs = ["That's not funny!", "This is not correct!"]

def IntInput(msg: str = 'Write an integer value: ', ermsg: str = 'is not integer.', empty_input: bool = False) -> int:
    """
    Prompts the user for input and validates it as an integer.

    The function repeatedly asks for input until a valid integer is provided.
    It does not allow empty inputs by default.

    Args:
        msg (str, optional): The message to display to the user.
        ermsg (str, optional): The error message to display on invalid input.
        empty-input (bool, optional): If True, allows empty inputs. Defaults to False.
    Returns:
        int: The integer value of the valid input.
    """
    while True:
        try:
            text = input(msg)
            if not empty_input and not text:
                print(emptymsg)
                continue
            if not text:
                break  
            text = int(text)
            break
        except ValueError:
            print(f'{text} {ermsg}')
            continue
        except KeyboardInterrupt:
            print(msgs[0])
            continue
        except EOFError:
            print(msgs[1])  
            continue       
    return text

def StrInput(msg: str = 'Write any string: ', empty_input: bool = False) -> str:
    """
    Prompts the user for input and validates it as a non-empty string.

    The function repeats the prompt until a non-empty string is provided.
    It does not allow empty inputs by default.

    Args:
        msg (str): The message to display to the user.
        empty-input (bool): If True, allows empty inputs. Defaults to False.
    Returns:
        str: The validated non-empty input string.
    """
    while True:
        try:
            text = input(msg)
            if not empty_input and not text:
                print(emptymsg)
                continue
            if not text:
                break  
            break
        except KeyboardInterrupt:
            print(msgs[0])
            continue
        except EOFError:
            print(msgs[1])  
            continue       
    return text

def FloatInput(msg: str = 'Write a float value: ', ermsg: str = 'is not float.', empty_input: bool = False) -> float:
    """
    Prompts the user for input and validates it as a float.

    The function repeatedly asks for input until a valid float is provided.
    It does not allow empty inputs by default.

    Args:
        msg (str): The message to display to the user.
        ermsg (str): The error message to display on invalid input.
        empty-input (bool): If True, allows empty inputs. Defaults to False.
    Returns:
        float: the float value of the input.
    """
    while True:
        try:
            text = input(msg)
            if not empty_input and not text:
                print(emptymsg)
                continue
            if not text:
                break  
            text = float(text)
            break
        except ValueError:
            print(f'{text} {ermsg}')
            continue
        except KeyboardInterrupt:
            print(msgs[0])
            continue
        except EOFError:
            print(msgs[1])  
            continue       
    return text

def multiInput(num: int, msg: str = 'Write any string: ', empty_input: bool = False) -> list:
    """
    Prompts the user for a specified number of inputs and returns them as a list.

    This function asks for 'n' inputs and collects them into a list.
    It does not allow empty inputs by default.

    Args:
        msg (str): the message display for each input prompt.
        empty-input (bool): If True, allows empty inputs. Defaults to False.
    Returns:
        list[str]: A list containing all the input strings.
    """
    inputs: list[str] = []
    aux : int = 0
    while True:
        try:
            while aux < num:
                text = input(msg)
                if not empty_input and not text:
                    print(emptymsg)
                    continue
                if not text:
                    inputs.append('')
                    aux += 1
                    continue  
                inputs.append(text)
                aux += 1
        except KeyboardInterrupt:
            print(msgs[0])
            continue
        except EOFError:
            print(msgs[1])
            continue
        return inputs