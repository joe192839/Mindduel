// static/quickplay/js/components/MatchHistoryTable.js

import React from 'react';

const MatchHistoryTable = () => {
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const formatTime = (startTime, endTime) => {
        if (!startTime || !endTime) return "N/A";
        const start = new Date(startTime);
        const end = new Date(endTime);
        const diffInSeconds = Math.floor((end - start) / 1000);
        const minutes = Math.floor(diffInSeconds / 60);
        const seconds = diffInSeconds % 60;
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    const formatCategories = (categories) => {
        if (!categories) return "All";
        return categories.split(',').map(cat => 
            cat.trim().split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')
        ).join(', ');
    };

    const getStatusColor = (score) => {
        if (score >= 80) return 'text-green-400';
        if (score >= 60) return 'text-blue-400';
        return 'text-red-400';
    };

    const getStatusText = (score) => {
        if (score >= 80) return 'Victory';
        if (score >= 60) return 'Completed';
        return 'Defeat';
    };

    return (
        <div className="bg-slate-800 rounded-xl overflow-hidden">
            <div className="p-6 border-b border-slate-700">
                <h3 className="text-xl font-semibold text-white">Match History</h3>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-slate-700">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Score</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Categories</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Time</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                        {window.matchHistory && window.matchHistory.map((match, index) => (
                            <tr key={index} className="hover:bg-slate-700 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                    {formatDate(match.start_time)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                    {match.score}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                    {formatCategories(match.categories)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                    {formatTime(match.start_time, match.end_time)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className={getStatusColor(match.score)}>
                                        {getStatusText(match.score)}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default MatchHistoryTable;