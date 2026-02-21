import React from 'react'
import './Message.css'

const Message = ({ message }) => {
  const isUser = message.sender === 'user'
  const isError = message.isError

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-bot'} ${isError ? 'message-error' : ''}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-text">{message.text}</div>
        <div className="message-time">{formatTime(message.timestamp)}</div>
      </div>
    </div>
  )
}

export default Message

