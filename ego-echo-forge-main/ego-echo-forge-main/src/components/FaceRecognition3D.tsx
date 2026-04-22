import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

// Creates a face-like point cloud mesh that morphs and glows
const FaceMesh = () => {
  const pointsRef = useRef<THREE.Points>(null);
  const count = 2000;

  const [positions, basePositions, colors] = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const basePositions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      // Create face-like oval shape with features
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      
      // Oval head shape
      let r = 1.2;
      const yFactor = Math.cos(phi);
      
      // Slightly elongate vertically for face shape
      let x = r * Math.sin(phi) * Math.cos(theta) * 0.85;
      let y = r * Math.cos(phi) * 1.2;
      let z = r * Math.sin(phi) * Math.sin(theta) * 0.5;

      // Eye socket indentations
      const eyeLeft = new THREE.Vector3(-0.3, 0.2, 0.4);
      const eyeRight = new THREE.Vector3(0.3, 0.2, 0.4);
      const pos = new THREE.Vector3(x, y, z);
      
      if (pos.distanceTo(eyeLeft) < 0.2 || pos.distanceTo(eyeRight) < 0.2) {
        z -= 0.1;
      }

      // Nose ridge
      if (Math.abs(x) < 0.08 && y > -0.1 && y < 0.3 && z > 0.2) {
        z += 0.15;
      }

      // Mouth area
      if (Math.abs(x) < 0.25 && y > -0.5 && y < -0.3 && z > 0.2) {
        z -= 0.05;
      }

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;
      basePositions[i * 3] = x;
      basePositions[i * 3 + 1] = y;
      basePositions[i * 3 + 2] = z;

      // Color: teal to cyan gradient with some purple highlights
      const distFromCenter = Math.sqrt(x * x + y * y);
      const t = distFromCenter / 1.5;
      colors[i * 3] = 0.1 + t * 0.4;     // R - more at edges
      colors[i * 3 + 1] = 0.6 + (1 - t) * 0.4; // G - more at center
      colors[i * 3 + 2] = 0.9;           // B - consistently high
    }

    return [positions, basePositions, colors];
  }, []);

  useFrame(({ clock }) => {
    if (!pointsRef.current) return;
    const t = clock.getElapsedTime();
    const pos = pointsRef.current.geometry.attributes.position.array as Float32Array;

    for (let i = 0; i < count; i++) {
      const bx = basePositions[i * 3];
      const by = basePositions[i * 3 + 1];
      const bz = basePositions[i * 3 + 2];

      // Breathing / pulsing effect
      const pulse = Math.sin(t * 1.5) * 0.03;
      // Wave distortion
      const wave = Math.sin(by * 3 + t * 2) * 0.02;
      // Particle drift
      const drift = Math.sin(t * 0.5 + i * 0.01) * 0.015;

      pos[i * 3] = bx * (1 + pulse) + drift;
      pos[i * 3 + 1] = by * (1 + pulse) + wave;
      pos[i * 3 + 2] = bz * (1 + pulse * 0.5);
    }

    pointsRef.current.geometry.attributes.position.needsUpdate = true;
    // Slow rotation
    pointsRef.current.rotation.y = Math.sin(t * 0.3) * 0.3;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        vertexColors
        transparent
        opacity={0.9}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
};

// Scanning lines effect around the face
const ScanLines = () => {
  const ref = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.rotation.z = clock.getElapsedTime() * 0.5;
    ref.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.3) * 0.2;
  });

  return (
    <mesh ref={ref}>
      <torusGeometry args={[1.6, 0.005, 8, 64]} />
      <meshBasicMaterial color="#14b8a6" transparent opacity={0.4} />
    </mesh>
  );
};

const ScanLines2 = () => {
  const ref = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.rotation.z = -clock.getElapsedTime() * 0.3;
    ref.current.rotation.y = Math.sin(clock.getElapsedTime() * 0.4) * 0.3;
  });

  return (
    <mesh ref={ref}>
      <torusGeometry args={[1.8, 0.003, 8, 64]} />
      <meshBasicMaterial color="#0ea5e9" transparent opacity={0.3} />
    </mesh>
  );
};

// Small orbiting dots
const OrbitDots = () => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.z = clock.getElapsedTime() * 0.8;
  });

  return (
    <group ref={groupRef}>
      {[0, Math.PI * 0.5, Math.PI, Math.PI * 1.5].map((angle, i) => (
        <mesh key={i} position={[Math.cos(angle) * 1.4, Math.sin(angle) * 1.4, 0]}>
          <sphereGeometry args={[0.03, 8, 8]} />
          <meshBasicMaterial color={i % 2 === 0 ? "#14b8a6" : "#8b5cf6"} />
        </mesh>
      ))}
    </group>
  );
};

const FaceRecognition3D = () => {
  return (
    <div className="w-72 h-72 md:w-96 md:h-96">
      <Canvas
        camera={{ position: [0, 0, 3.5], fov: 50 }}
        dpr={[1, 2]}
        gl={{ alpha: true, antialias: true }}
        style={{ background: "transparent" }}
      >
        <ambientLight intensity={0.5} />
        <FaceMesh />
        <ScanLines />
        <ScanLines2 />
        <OrbitDots />
      </Canvas>
    </div>
  );
};

export default FaceRecognition3D;
