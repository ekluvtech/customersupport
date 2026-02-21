import React from 'react'
import './LoadingIndicator.css'

const LoadingIndicator = () => {
  return (
    <div className="loading-indicator">
      <div className="message message-bot">
        <div className="message-avatar">🤖</div>
        <div className="message-content">
          <div className="message-text loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoadingIndicator

