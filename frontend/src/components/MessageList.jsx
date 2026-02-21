import React from 'react'
import Message from './Message'
import LoadingIndicator from './LoadingIndicator'
import './MessageList.css'

const MessageList = ({ messages, isLoading }) => {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      {isLoading && <LoadingIndicator />}
    </div>
  )
}

export default MessageList

