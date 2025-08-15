AUTHENTICATED_USER_SUBSCRIPTION = """
    subscription {
            testAuthenticatedUser {
                __typename
                ... on UnauthenticatedError {
                    message
                }
                ...on Error {
                    message
                }
                ... on User {
                    userUuid
                }
            }
        }
"""

INDENT_EVENTS_SUBSCRIPTION = """
  subscription ChatEvents(
    $prompt: Prompt
    $chatUuid: String!
    $parentUuid: String
    $model: ModelName!
    $strategyNameOverride: StrategyName
    $depthLimit: Int!
    $requireConfirmation: Boolean
    $readOnly: Boolean
    $enableThinking: Boolean
  ) {
    indentChat(
      chatInput: {
        prompt: $prompt
      }
      parentUuid: $parentUuid
      chatConfig: {
        chatUuid: $chatUuid
        model: $model
        requireConfirmation: $requireConfirmation
        readOnly: $readOnly
        strategyNameOverride: $strategyNameOverride
        depthLimit: $depthLimit
        enableThinking: $enableThinking
      }
    ) {
      __typename
      ...on Error {
        message
      }
      ...on UnauthenticatedError {
        message
      }
      ...on UserEvent {
        uuid
        parentUuid
        chatId
        isSidechain
        version
        createdAt
        sidechainRootUuid
        synthetic
        messageData: message {
          __typename
          ... on TextMessage {
            text
          }
          ... on ToolResultMessage {
            messageId
            toolUseId
            text
            resultData {
              ... on BashToolResult {
                shellOutput
                exitCode
              }
              ... on ReadToolResult {
                content
              }
            }
          }
           ... on ToolCallMessage {
            messageId
            toolUseId
            toolName
            toolInput {
              ... on BashToolInput {
                command
              }
              ... on ReadToolInput {
                filePath
              }
            }
          }
          ... on PartialToolResultMessage {
            messageId
            toolUseId
            text
            resultData {
              ... on PartialToolResult {
                __typename
              }
            }
          }
        }
      }
      ...on AssistantEvent {
        uuid
        parentUuid
        chatId
        isSidechain
        version
        createdAt
        sidechainRootUuid
        synthetic
        messageData: message {
          __typename
          ... on TextMessage {
            text
          }
          ... on ToolCallMessage {
            messageId
            toolUseId
            toolName
            toolInput {
              ... on BashToolInput {
                command
              }
              ... on ReadToolInput {
                filePath
              }
            }
          }
        }
      }
      ...on SystemEvent {
        uuid
        parentUuid
        chatId
        isSidechain
        version
        createdAt
        sidechainRootUuid
        messageData: message {
          __typename
          ... on ToolCallMessage {
            messageId
            toolUseId
            toolName
            toolInput {
              ... on BashToolInput {
                command
              }
              ... on ReadToolInput {
                filePath
              }
            }
          }
          ... on ToolResultMessage {
            messageId
            toolUseId
            text
            resultData {
              ... on BashToolResult {
                shellOutput
                exitCode
              }
              ... on ReadToolResult {
                content
              }
            }
          }
          ... on ToolExecutionStatusMessage {
            executionStatus: status
          }
          ... on ToolPermissionStatusMessage {
            permissionStatus: status
          }
        }
      }
    }
  }
"""


CONFIRM_AND_CONTINUE_SUBSCRIPTION = """
  subscription ChatEvents(
    $requestUuid: String!
    $chatUuid: String!
    $model: ModelName!
    $strategyNameOverride: StrategyName
    $depthLimit: Int!
    $requireConfirmation: Boolean
    $readOnly: Boolean
    $enableThinking: Boolean
  ) {
    confirmAndContinue(
      requestEventUuid: $requestUuid
      chatConfig: {
        chatUuid: $chatUuid
        model: $model
        requireConfirmation: $requireConfirmation
        readOnly: $readOnly
        strategyNameOverride: $strategyNameOverride
        depthLimit: $depthLimit
        enableThinking: $enableThinking
      }
    ) {
      __typename
      ...on Error {
        message
      }
      ...on UnauthenticatedError {
        message
      }
      ...on UserEvent {
        uuid
        parentUuid
        chatId
        isSidechain
        version
        createdAt
        sidechainRootUuid
        synthetic
        messageData: message {
          __typename
          ... on TextMessage {
            text
          }
          ... on ToolResultMessage {
            messageId
            toolUseId
            text
            resultData {
              ... on BashToolResult {
                shellOutput
                exitCode
              }
              ... on ReadToolResult {
                content
              }
            }
          }
          ... on PartialToolResultMessage {
            messageId
            toolUseId
            text
            resultData {
              ... on PartialToolResult {
                __typename
              }
            }
          }
        }
      }
      ...on AssistantEvent {
        uuid
        parentUuid
        chatId
        isSidechain
        version
        createdAt
        sidechainRootUuid
        synthetic
        messageData: message {
          __typename
          ... on TextMessage {
            text
          }
          ... on ToolCallMessage {
            messageId
            toolUseId
            toolName
            toolInput {
              ... on BashToolInput {
                command
              }
              ... on ReadToolInput {
                filePath
              }
            }
          }
        }
      }
      ...on SystemEvent {
        uuid
        parentUuid
        chatId
        isSidechain
        version
        createdAt
        sidechainRootUuid
        messageData: message {
          __typename
          ... on ToolCallMessage {
            messageId
            toolUseId
            toolName
            toolInput {
              ... on BashToolInput {
                command
              }
              ... on ReadToolInput {
                filePath
              }
            }
          }
          ... on ToolResultMessage {
            messageId
            toolUseId
            text
            resultData {
              ... on BashToolResult {
                shellOutput
                exitCode
              }
              ... on ReadToolResult {
                content
              }
            }
          }
          ... on ToolExecutionStatusMessage {
            executionStatus: status
          }
          ... on ToolPermissionStatusMessage {
            permissionStatus: status
          }
        }
      }
    }
  }
"""


INDENT_CHAT_EVENT_STREAM_SUBSCRIPTION = """
  subscription IndentChatEventStream(
    $chatUuid: String!
    $lastKnownFullEventUuid: String
  ) {
    indentChatEventStream(
      chatUuid: $chatUuid
      lastKnownFullEventUuid: $lastKnownFullEventUuid
    ) {
      __typename
      ...on Error {
        message
      }
      ...on UnauthenticatedError {
        message
      }
      ...on UserEvent {
        uuid
        parentUuid
        chatId
        isSidechain
        version
        createdAt
        sidechainRootUuid
        synthetic
        messageData: message {
          __typename
          ... on TextMessage {
            text
          }
          ... on ToolResultMessage {
            messageId
            toolUseId
            text
            resultData {
              ... on BashToolResult {
                shellOutput
                exitCode
              }
              ... on ReadToolResult {
                content
              }
            }
          }
          ... on PartialToolResultMessage {
            messageId
            toolUseId
            text
            resultData {
              ... on PartialToolResult {
                __typename
              }
            }
          }
        }
      }
      ...on AssistantEvent {
        uuid
        parentUuid
        chatId
        isSidechain
        version
        createdAt
        sidechainRootUuid
        synthetic
        messageData: message {
          __typename
          ... on TextMessage {
            text
          }
          ... on ToolCallMessage {
            messageId
            toolUseId
            toolName
            toolInput {
              ... on BashToolInput {
                command
              }
              ... on ReadToolInput {
                filePath
              }
            }
          }
        }
      }
      ...on SystemEvent {
        uuid
        parentUuid
        chatId
        isSidechain
        version
        createdAt
        sidechainRootUuid
        messageData: message {
          __typename
          ... on ToolCallMessage {
            messageId
            toolUseId
            toolName
            toolInput {
              ... on BashToolInput {
                command
              }
              ... on ReadToolInput {
                filePath
              }
            }
          }
          ... on ToolResultMessage {
            messageId
            toolUseId
            text
            resultData {
              ... on BashToolResult {
                shellOutput
                exitCode
              }
              ... on ReadToolResult {
                content
              }
            }
          }
          ... on ToolExecutionStatusMessage {
            executionStatus: status
          }
          ... on ToolPermissionStatusMessage {
            permissionStatus: status
          }
        }
      }
    }
  }
"""
