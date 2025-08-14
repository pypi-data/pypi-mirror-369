import io
import os
import json
import mimetypes
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# ==============================================================================
#  1. THE REUSABLE API CLIENT CLASS
# ==============================================================================

class GoogleApiClient:
	"""
	A client to interact with Google Drive, Sheets, and Publisher APIs.
	Manages services and authentication in a self-contained object.
	"""
	def __init__(self, credentials_dict, verbose=False):
		"""
		Initializes the client with service account credentials.

		Args:
			credentials_dict (dict): A dictionary of the service account JSON key.
			verbose (bool): If True, prints status messages for operations.
		"""
		if not isinstance(credentials_dict, dict) or 'client_email' not in credentials_dict:
			raise ValueError("A valid service account credentials dictionary is required.")
		
		self.creds_dict = credentials_dict
		self.verbose = verbose

		# Private placeholders for services (will be lazy-loaded)
		self._drive_service = None
		self._gspread_service = None
		self._publisher_service = None

	def _get_creds(self, scopes):
		"""Helper to create credentials for specific scopes."""
		return ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, scopes)

	@property
	def drive_service(self):
		"""Lazy-loads and returns the Google Drive API service client."""
		if not self._drive_service:
			creds = self._get_creds(['https://www.googleapis.com/auth/drive'])
			self._drive_service = build('drive', 'v3', credentials=creds)
			if self.verbose: print("[Client] Google Drive service initialized.")
		return self._drive_service

	@property
	def gspread_service(self):
		"""Lazy-loads and returns the gspread service client."""
		if not self._gspread_service:
			creds = self._get_creds(['https://www.googleapis.com/auth/drive'])
			self._gspread_service = gspread.authorize(creds)
			if self.verbose: print("[Client] gspread service initialized.")
		return self._gspread_service

	@property
	def publisher_service(self):
		"""Lazy-loads and returns the Android Publisher API service client."""
		if not self._publisher_service:
			creds = self._get_creds(['https://www.googleapis.com/auth/androidpublisher'])
			self._publisher_service = build('androidpublisher', 'v3', credentials=creds)
			if self.verbose: print("[Client] Android Publisher service initialized.")
		return self._publisher_service

	def _get_file_by_name(self, name):
		"""
		Internal helper to find a single file or folder by its exact name.
		Raises FileNotFoundError or ValueError for invalid states.
		"""
		query = f"name = '{name}' and trashed = false"
		results = self.drive_service.files().list(q=query, fields="files(id, name, parents)").execute()
		files = results.get('files', [])

		if not files:
			raise FileNotFoundError(f"No file or folder found with name: '{name}'")
		if len(files) > 1:
			raise ValueError(f"More than one item found with name: '{name}'")
		
		return files[0]

	def download_file_by_name(self, file_name):
		"""Downloads a file's content given its name."""
		if self.verbose: print(f"Searching for file '{file_name}'...")
		file_info = self._get_file_by_name(file_name)
		file_id = file_info['id']
		
		if self.verbose: print(f"Found file ID: {file_id}. Downloading content...")
		request = self.drive_service.files().get_media(fileId=file_id)
		data = io.BytesIO()
		downloader = MediaIoBaseDownload(data, request)
		
		done = False
		while not done:
			status, done = downloader.next_chunk()
			if self.verbose: print(f"Download {int(status.progress() * 100)}%")
		
		return data.getvalue().decode('utf-8')

	def list_files(self, folder_name=None):
		"""Lists files and folders, optionally within a specific folder."""
		query = ""
		if folder_name:
			if self.verbose: print(f"Finding folder '{folder_name}'...")
			folder_info = self._get_file_by_name(folder_name)
			query = f"'{folder_info['id']}' in parents and trashed = false"
		
		results = self.drive_service.files().list(
			q=query,
			fields="nextPageToken, files(id, name, mimeType)",
			pageSize=100
		).execute()
		return results.get('files', [])

	def upload_file(self, local_data, destination_name, destination_folder=None):
		"""
		Uploads data to a file on Google Drive.
		Updates the file if it exists, otherwise creates it.
		Optionally places it in a specified folder.
		"""
		# Determine MIME type automatically
		mime_type, _ = mimetypes.guess_type(destination_name)
		if mime_type is None:
			mime_type = 'application/octet-stream' # Default binary type
		
		media = MediaIoBaseUpload(io.BytesIO(local_data.encode('utf-8')), mimetype=mime_type, resumable=True)
		
		try:
			# Check if file exists to update it
			existing_file = self._get_file_by_name(destination_name)
			if self.verbose: print(f"File '{destination_name}' exists. Updating...")
			results = self.drive_service.files().update(
				fileId=existing_file['id'],
				media_body=media
			).execute()
			message = "File updated"
		except FileNotFoundError:
			# File doesn't exist, so create it
			if self.verbose: print(f"File '{destination_name}' not found. Creating...")
			file_metadata = {'name': destination_name}
			results = self.drive_service.files().create(
				body=file_metadata,
				media_body=media,
				fields='id',
				supportsAllDrives=True
			).execute()
			message = "File created"

		file_id = results.get('id')
		if self.verbose: print(f"{message}: {results}")

		if destination_folder:
			self.move_file(destination_name, destination_folder)
		
		return file_id

	def delete_file_by_name(self, file_name):
		"""Finds a file by name and deletes it."""
		if self.verbose: print(f"Finding '{file_name}' to delete...")
		file_info = self._get_file_by_name(file_name)
		self.drive_service.files().delete(fileId=file_info['id']).execute()
		if self.verbose: print(f"File '{file_name}' (ID: {file_info['id']}) deleted successfully.")

	def move_file(self, file_name, folder_name):
		"""Moves a file to a specified folder."""
		if self.verbose: print(f"Moving '{file_name}' to folder '{folder_name}'...")
		file_info = self._get_file_by_name(file_name)
		folder_info = self._get_file_by_name(folder_name)

		# Retrieve the file's existing parents to remove them
		previous_parents = ",".join(file_info.get('parents', []))

		self.drive_service.files().update(
			fileId=file_info['id'],
			addParents=folder_info['id'],
			removeParents=previous_parents,
			fields='id, parents'
		).execute()
		if self.verbose: print("Move complete.")


# ==============================================================================
#  2. THE COMMAND-LINE INTERFACE (CLI)
# ==============================================================================

def main_cli():
	"""Runs the interactive command-line application."""
	creds_path = 'credentials.json' # Assumes credentials are in this file
	
	try:
		with open(creds_path) as f:
			creds_dict = json.load(f)
	except (FileNotFoundError, json.JSONDecodeError):
		print(f"ERROR: Credentials file not found or invalid. Please create '{creds_path}'.")
		return

	client = GoogleApiClient(creds_dict, verbose=True)
	print("\nGoogle API Client Initialized. Type 'help' for commands.")

	while True:
		try:
			command_str = input(">> ").strip()
			if not command_str:
				continue

			parts = command_str.split(maxsplit=2)
			action = parts[0].lower()
			
			if action == 'exit':
				break
			
			elif action == 'help':
				print("Commands:\n"
					  "  open <filename>\t\t- Download and print file content\n"
					  "  list [foldername]\t\t- List files in root or a folder\n"
					  "  save <filename> <data>\t- Save data to a file\n"
					  "  delete <filename>\t\t- Delete a file\n"
					  "  move <filename> <foldername>\t- Move a file to a folder\n"
					  "  exit\t\t\t\t- Close the application")

			elif action == 'open':
				file_content = client.download_file_by_name(parts[1])
				print("-" * 20 + f"\n{file_content}\n" + "-" * 20)

			elif action == 'list':
				folder = parts[1] if len(parts) > 1 else None
				files = client.list_files(folder)
				if not files:
					print("No files found.")
				else:
					for item in files:
						print(f"- {item['name']} ({item['mimeType']})")
			
			elif action == 'save':
				client.upload_file(local_data=parts[2], destination_name=parts[1])
			
			elif action == 'delete':
				client.delete_file_by_name(parts[1])
			
			elif action == 'move':
				client.move_file(file_name=parts[1], folder_name=parts[2])

			else:
				print(f"Unknown command: '{action}'. Type 'help' for options.")

		except IndexError:
			print("Error: Not enough arguments for the command. Type 'help'.")
		except (FileNotFoundError, ValueError, gspread.exceptions.SpreadsheetNotFound) as e:
			print(f"ERROR: {e}")
		except Exception as e:
			print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
	main_cli()