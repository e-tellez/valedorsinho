interface StepIndicatorProps {
  currentStep: number;
  totalSteps?: number;
}

export default function StepIndicator({
  currentStep,
  totalSteps = 4,
}: StepIndicatorProps) {
  return (
    <div className="flex items-center mb-6">
      {Array.from({ length: totalSteps }, (_, i) => {
        const step = i + 1;
        const isActive = step === currentStep;
        const isCompleted = step < currentStep;
        return (
          <div key={step} className={`flex items-center ${step < totalSteps ? "flex-1" : ""}`}>
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-[0.8rem] font-bold shrink-0
                ${isActive ? "bg-primary text-white" : "bg-gray-200 text-gray-500"}`}
            >
              {step}
            </div>
            {step < totalSteps && (
              <div className={`flex-1 h-0.5 mx-2 ${step < currentStep ? "bg-primary" : "bg-gray-200"}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
