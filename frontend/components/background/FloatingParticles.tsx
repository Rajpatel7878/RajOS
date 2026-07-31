"use client";

const particles = [
  { left: "10%", top: "20%" },
  { left: "25%", top: "70%" },
  { left: "40%", top: "15%" },
  { left: "55%", top: "80%" },
  { left: "70%", top: "35%" },
  { left: "85%", top: "65%" },
  { left: "15%", top: "90%" },
  { left: "90%", top: "15%" },
  { left: "50%", top: "50%" },
  { left: "30%", top: "40%" },
  { left: "75%", top: "85%" },
  { left: "60%", top: "10%" },
];

export default function FloatingParticles() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">

      {particles.map((particle, index) => (
        <span
          key={index}
          className="absolute h-1.5 w-1.5 rounded-full bg-cyan-400/40 animate-float"
          style={{
            left: particle.left,
            top: particle.top,
            animationDelay: `${index * 0.3}s`,
          }}
        />
      ))}

    </div>
  );
}
