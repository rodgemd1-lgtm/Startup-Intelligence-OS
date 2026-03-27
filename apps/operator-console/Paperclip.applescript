-- Paperclip.app — Launch the cost dashboard
-- Starts the server if not running, opens browser

on run
	set serverPort to 4174
	set serverScript to (POSIX path of (path to home folder)) & "Startup-Intelligence-OS/apps/operator-console/paperclip-server.py"
	set dashURL to "http://localhost:" & serverPort

	-- Check if server is already running
	try
		do shell script "lsof -ti:" & serverPort
		-- Server running, just open browser
	on error
		-- Start server in background
		do shell script "cd " & quoted form of (POSIX path of (path to home folder)) & "Startup-Intelligence-OS/apps/operator-console && /usr/bin/python3 " & quoted form of serverScript & " &> /dev/null &"
		delay 1
	end try

	-- Open in default browser
	open location dashURL
end run
