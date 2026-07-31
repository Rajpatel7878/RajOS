"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import {
  Float,
  OrbitControls,
  Sphere,
  Stars,
} from "@react-three/drei";

import { useRef } from "react";
import * as THREE from "three";


function Core(){

const mesh = useRef<THREE.Mesh>(null);


useFrame((state)=>{

if(mesh.current){

mesh.current.rotation.y += 0.008;
mesh.current.rotation.x =
Math.sin(state.clock.elapsedTime)*0.2;

}

});


return(

<>

<Float
speed={2}
rotationIntensity={1}
floatIntensity={2}
>


<Sphere
ref={mesh}
args={[1.2,128,128]}
>

<meshStandardMaterial

color="#22d3ee"

emissive="#06b6d4"

emissiveIntensity={5}

metalness={1}

roughness={0.15}

/>

</Sphere>


</Float>


</>

)

}



export default function AIOrb3D(){

return(

<div className="h-[500px] w-full">


<Canvas
camera={{
position:[0,0,4],
fov:45
}}
>


<ambientLight intensity={1}/>


<pointLight
position={[3,3,3]}
intensity={8}
color="#22d3ee"
/>


<pointLight
position={[-3,-3,-3]}
intensity={5}
color="#8b5cf6"
/>


<Stars
radius={5}
depth={20}
count={300}
factor={3}
/>


<Core />


<OrbitControls
enableZoom={false}
/>


</Canvas>


</div>


)

}
