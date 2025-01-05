const BrainWarmup = ({ onComplete }) => {
    const { Brain, Zap, ChevronRight } = lucide;
    const [phase, setPhase] = React.useState(0);
  
    React.useEffect(() => {
      const phases = [
        setTimeout(() => setPhase(1), 1000),
        setTimeout(() => setPhase(2), 2000),
        setTimeout(() => setPhase(3), 3000),
        setTimeout(() => setPhase(4), 4000)
      ];
  
      setTimeout(() => {
        if (onComplete) onComplete();
      }, 5000);
  
      return () => phases.forEach(clearTimeout);
    }, []);
  
    if (phase === -1) return null;
  
    return (
      <div className="fixed inset-0 bg-black/95 flex items-center justify-center z-50">
        <div className="text-center">
          <div className="relative mb-8">
            <Brain
              className={`w-32 h-32 mx-auto transition-all duration-700 ${
                phase > 0 ? 'text-[#009fdc] scale-110' : 'text-gray-600'
              }`}
            />
            {phase > 1 && (
              <div className="absolute inset-0 flex items-center justify-center">
                {[...Array(3)].map((_, i) => (
                  <Zap
                    key={i}
                    className="w-8 h-8 text-yellow-400 animate-pulse"
                    style={{
                      position: 'absolute',
                      transform: `rotate(${i * 120}deg) translateY(-20px)`
                    }}
                  />
                ))}
              </div>
            )}
          </div>
          <div className="space-y-4">
            <h2 className={`text-3xl font-bold transition-all duration-500 ${
              phase > 0 ? 'text-[#009fdc]' : 'text-gray-600'
            }`}>
              {phase === 0 && "Initializing..."}
              {phase === 1 && "Brain Engaged"}
              {phase === 2 && "Synapses Firing"}
              {phase === 3 && "Ready For Challenge"}
              {phase === 4 && (
                <div className="flex items-center justify-center gap-2">
                  <span>GO</span>
                  <ChevronRight className="animate-bounce" />
                </div>
              )}
            </h2>
            <div className="flex justify-center gap-2">
              {[...Array(4)].map((_, i) => (
                <div
                  key={i}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    i < phase ? 'bg-[#009fdc] scale-110' : 'bg-gray-600'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  export default BrainWarmup;