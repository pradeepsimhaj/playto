import { Menu, Search } from "lucide-react";

export default function Navbar({ title, onSearch }) {
  return (
    <div className="w-full bg-white shadow px-4 py-3 flex items-center justify-between sticky top-0 z-10">
      
      {/* Left */}
      <div className="flex items-center gap-3">
        <Menu className="md:hidden" />
        <h1 className="text-lg md:text-xl font-semibold">{title}</h1>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2 bg-gray-100 px-3 py-1 rounded w-40 md:w-64">
        <Search size={16} />
        <input
          placeholder="Search..."
          className="bg-transparent outline-none w-full text-sm"
          onChange={(e) => onSearch && onSearch(e.target.value)}
        />
      </div>
    </div>
  );
}