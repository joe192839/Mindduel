import React, { useState, useEffect } from 'react';

/**
 * TimeTransitionPreview Component
 * Displays a visual transition when the time limit changes between question groups
 * 
 * @param {Object} props
 * @param {number} props.oldTime - Previous time limit in seconds
 * @param {number} props.newTime - New time limit in seconds
 * @param {function} props.onTransitionComplete - Callback fired when transition ends
 * @param {number} props.circumference - Circumference of the progress circle
 */
const TimeTransitionPreview = ({ 
    oldTime = 60,  
    newTime = 50,  
    onTransitionComplete,
    circumference = 628.32  // 2 * π * 100 (default radius)
}) => {
    // Track the current count for animation
    const [count, setCount] = useState(oldTime);
    // State to control fade out animation
    const [fadeOut, setFadeOut] = useState(false);
    
    useEffect(() => {
        // Animate the countdown from old time to new time
        const countInterval = setInterval(() => {
            setCount(prev => {
                if (prev <= newTime) {
                    clearInterval(countInterval);
                    return prev;
                }
                return prev - 1;
            });
        }, 50);  // Updates every 50ms for smooth animation

        // Start fade out animation after 2.5s
        const fadeTimeout = setTimeout(() => {
            setFadeOut(true);
        }, 2500);

        // Trigger completion callback after 3s
        const completeTimeout = setTimeout(() => {
            if (onTransitionComplete) {
                onTransitionComplete();
            }
        }, 3000);

        // Cleanup timers on component unmount
        return () => {
            clearInterval(countInterval);
            clearTimeout(fadeTimeout);
            clearTimeout(completeTimeout);
        };
    }, [newTime, onTransitionComplete]);

    // Calculate circle progress
    const progress = (count / oldTime) * 100;
    const offset = circumference - (progress / 100) * circumference;

    // Determine color based on time remaining
    const getColor = (time) => {
        if (time > 30) return '#22c55e';    // Green for comfortable time
        if (time > 15) return '#eab308';    // Yellow for warning
        return '#dc2626';                    // Red for critical
    };

    return (
        <div className={`fixed inset-0 flex items-center justify-center bg-black bg-opacity-70 
            transition-opacity duration-500 ${fadeOut ? 'opacity-0' : 'opacity-100'}`}>
            <div className="text-center">
                {/* Timer Circle Container */}
                <div className="relative w-48 h-48 mx-auto mb-8">
                    <svg className="transform -rotate-90 w-48 h-48">
                        {/* Background Circle */}
                        <circle 
                            cx="96" 
                            cy="96" 
                            r="90" 
                            stroke="#334155"
                            strokeWidth="12"
                            fill="none"
                        />
                        {/* Progress Circle */}
                        <circle 
                            cx="96" 
                            cy="96" 
                            r="90"
                            stroke={getColor(count)}
                            strokeWidth="12"
                            fill="none"
                            strokeLinecap="round"
                            style={{
                                strokeDasharray: circumference,
                                strokeDashoffset: offset,
                                transition: 'stroke-dashoffset 0.5s ease-in-out, stroke 0.5s ease-in-out'
                            }}
                        />
                    </svg>
                    {/* Timer Text */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-4xl font-bold text-white">
                            {count}s
                        </span>
                    </div>
                </div>
                {/* Message Container */}
                <div className="space-y-2 text-white">
                    <p className="text-xl font-bold">Time Limit Changed!</p>
                    <p className="text-lg text-gray-300">
                        New time per question: {newTime}s
                    </p>
                </div>
            </div>
        </div>
    );
};

export default TimeTransitionPreview;