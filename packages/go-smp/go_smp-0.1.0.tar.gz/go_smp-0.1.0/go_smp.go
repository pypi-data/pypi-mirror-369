package main

import "C"

import (
	"fmt"
	"os"

	"github.com/aws/session-manager-plugin/src/datachannel"
	"github.com/aws/session-manager-plugin/src/log"
	"github.com/aws/session-manager-plugin/src/sessionmanagerplugin/session"
	_ "github.com/aws/session-manager-plugin/src/sessionmanagerplugin/session/portsession"
	_ "github.com/aws/session-manager-plugin/src/sessionmanagerplugin/session/shellsession"
)

//export StartSession
func StartSession(sessionId string, url string, tokenValue string, endpoint string, clientId string, targetId string) int {
	// Simple implementation of StartSession from session-manager-plugin, for POC purposes right now
	ssmSession := new(session.Session)
	ssmSession.SessionId = sessionId
	ssmSession.StreamUrl = url
	ssmSession.TokenValue = tokenValue
	ssmSession.Endpoint = endpoint
	ssmSession.ClientId = clientId
	ssmSession.TargetId = targetId
	ssmSession.DataChannel = &datachannel.DataChannel{}
	err := ssmSession.Execute(log.Logger(false, clientId))
	if err != nil {
		fmt.Fprintln(os.Stderr, "StartSession error:", err)
		return 1
	}
	return 0
}

func main() {}
