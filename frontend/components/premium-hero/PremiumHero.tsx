"use client";

import { motion } from "framer-motion";
import AICore from "./AICore";

export default function PremiumHero() {
  return (
    <section
      className="
      relative
      mx-auto
      grid
      min-h-[calc(100vh-80px)]
      max-w-7xl
      grid-cols-1
      items-center
      gap-12
      px-6
      py-20
      lg:grid-cols-2
      "
    >

      {/* Left Content */}

      <div>


        <motion.p
          initial={{opacity:0,y:20}}
          animate={{opacity:1,y:0}}
          transition={{duration:.6}}
          className="
          mb-6
          text-sm
          font-semibold
          uppercase
          tracking-[0.4em]
          text-cyan-400
          "
        >
          NEXT GENERATION AI OS
        </motion.p>



        <motion.h1
          initial={{opacity:0,y:40}}
          animate={{opacity:1,y:0}}
          transition={{duration:.8}}
          className="
          text-5xl
          font-extrabold
          leading-tight
          md:text-7xl
          "
        >

          Your Personal
          <br />

          <span className="text-gradient">
            AI Operating System
          </span>

        </motion.h1>



        <motion.p
          initial={{opacity:0,y:30}}
          animate={{opacity:1,y:0}}
          transition={{delay:.3}}
          className="
          mt-8
          max-w-xl
          text-lg
          text-slate-400
          "
        >

          RajOS combines AI memory, automation and intelligent
          workflows into one powerful personal workspace.

        </motion.p>



        <motion.div
          initial={{opacity:0,y:20}}
          animate={{opacity:1,y:0}}
          transition={{delay:.5}}
          className="
          mt-10
          flex
          gap-5
          "
        >

          <button
            className="
            rounded-xl
            bg-cyan-400
            px-8
            py-4
            font-bold
            text-black
            shadow-lg
            shadow-cyan-500/30
            transition
            hover:scale-105
            "
          >
            Launch RajOS
          </button>


          <button
            className="
            rounded-xl
            border
            border-white/20
            bg-white/5
            px-8
            py-4
            font-bold
            text-white
            backdrop-blur-xl
            transition
            hover:scale-105
            "
          >
            Explore AI
          </button>


        </motion.div>



        <div
          className="
          mt-12
          grid
          grid-cols-3
          gap-6
          "
        >

          <Stat title="10K+" text="Users" />
          <Stat title="99%" text="Accuracy" />
          <Stat title="24/7" text="AI Support" />

        </div>


      </div>



      {/* Right AI Core */}

      <div>
        <AICore />
      </div>


    </section>
  );
}



function Stat({
  title,
  text,
}:{
  title:string;
  text:string;
}){

return(

<div
className="
rounded-2xl
border
border-white/10
bg-white/5
p-4
backdrop-blur-xl
"
>

<h3 className="text-2xl font-bold text-white">
{title}
</h3>

<p className="text-sm text-slate-400">
{text}
</p>

</div>

)

}
