"use client";

import { motion } from "framer-motion";

export default function NeuralGrid(){

return (

<div
className="
pointer-events-none
absolute
inset-0
overflow-hidden
"
>


{/* Grid */}

<div
className="
absolute
inset-0
bg-[linear-gradient(rgba(6,182,212,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.08)_1px,transparent_1px)]
bg-[size:60px_60px]
[mask-image:radial-gradient(circle_at_center,black,transparent_75%)]
"
/>



{/* Moving Light */}

<motion.div

animate={{
x:["-20%","120%"],
}}

transition={{
duration:12,
repeat:Infinity,
ease:"linear"
}}

className="
absolute
top-0
h-full
w-96
bg-gradient-to-r
from-transparent
via-cyan-400/20
to-transparent
blur-3xl
"

/>



{/* Purple Glow */}

<motion.div

animate={{
scale:[1,1.3,1],
opacity:[0.3,0.7,0.3]
}}

transition={{
duration:6,
repeat:Infinity
}}

className="
absolute
left-1/2
top-1/3
h-[500px]
w-[500px]
-translate-x-1/2
rounded-full
bg-violet-500/20
blur-[120px]
"

/>



</div>

);

}
