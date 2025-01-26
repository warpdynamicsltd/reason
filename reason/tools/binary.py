import subprocess
import logging

def run_binary(binary_path, input_string, *args):
    """
    Run a binary with a string passed to its standard input and return the output.
    
    :param binary_path: Path to the binary to execute.
    :param input_string: String to send to the binary's stdin.
    :param args: Arguments to pass to the binary.
    :return: The output of the binary (stdout).
    """
    try:
      # Construct the command
      command = [binary_path] + list(args)
      
      # Run the binary and pass the input string
      result = subprocess.run(
          command,
          input=input_string,   # Pass the string to stdin
          capture_output=True,  # Capture both stdout and stderr
          text=True,            # Decode input/output as text
          check=True            # Raise CalledProcessError on non-zero exit
      )

      logging.debug(result.stdout)
      
      # Return the output (stdout)
      return result.stdout.strip()
    
    except subprocess.CalledProcessError as e:
      # Handle errors in execution
      print(f"Error: {e.stderr.strip()}")
      raise e
    except FileNotFoundError:
      # Handle case where binary does not exist
      print(f"Error: Binary not found at {binary_path}")
      # raise


